# app/services/chat_service.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
import time
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.models.message import RoleEnum
from app.services.llm_service import llm_service
from app.services.search_service import search_service


class ChatService:
    def __init__(self, db: Session):
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.db = db

    def create_conversation(self, user_id: int, title: str = None):
        """Create a new conversation"""
        print(f"[CHAT] Creating conversation for user {user_id}")
        return self.conversation_repo.create(user_id, title)

    def get_conversation(self, conversation_id: int, user_id: int):
        """Get conversation details"""
        print(f"[CHAT] Getting conversation {conversation_id} for user {user_id}")
        conversation = self.conversation_repo.get_by_id(conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

    def get_user_conversations(self, user_id: int) -> List:
        """Get all conversations for user"""
        print(f"[CHAT] Getting all conversations for user {user_id}")
        return self.conversation_repo.get_all_by_user(user_id)

    def delete_conversation(self, conversation_id: int, user_id: int):
        """Delete a conversation"""
        print(f"[CHAT] Deleting conversation {conversation_id}")
        conversation = self.get_conversation(conversation_id, user_id)
        self.conversation_repo.delete(conversation)

    def send_message(
        self,
        conversation_id: int,
        user_id: int,
        query: str,
        document_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response with citations
        """
        print(f"\n[CHAT] === NEW MESSAGE ===")
        print(f"[CHAT] Conversation: {conversation_id}, User: {user_id}")
        print(f"[CHAT] Query: {query}")
        print(f"[CHAT] Document IDs: {document_ids}")
        
        start_time = time.time()
        
        # Verify conversation belongs to user
        print(f"[CHAT] Verifying conversation access...")
        conversation = self.get_conversation(conversation_id, user_id)
        
        try:
            # Save user message
            print(f"[CHAT] Saving user message...")
            user_message = self.message_repo.create(
                conversation_id=conversation_id,
                role=RoleEnum.user,
                content=query
            )
            print(f"[CHAT] User message saved (ID: {user_message.id})")
            
            # Search for relevant context - pass db session to search_service
            print(f"[CHAT] Searching for relevant documents...")
            search_service.db = self.db  # Set db session for document title lookup
            search_start = time.time()
            raw_citations = search_service.search_documents(query, user_id, document_ids=document_ids)
            search_time = time.time() - search_start
            print(f"[CHAT] Search completed in {search_time:.2f}s, found {len(raw_citations)} results")
            
            if raw_citations:
                for i, c in enumerate(raw_citations[:2]):
                    print(f"[CHAT]   Result {i+1}: {c.get('documentTitle', 'N/A')} page {c.get('page', 'N/A')}")
            
            # Build context from citations
            print(f"[CHAT] Building context from {len(raw_citations)} citations...")
            context_parts = []
            for i, c in enumerate(raw_citations[:5]):
                snippet = c.get('snippet', '')
                title = c.get('documentTitle', 'Unknown')
                page = c.get('page', 1)
                print(f"[CHAT]   Citation {i+1}: {title} (page {page}, len={len(snippet)})")
                if snippet:
                    context_parts.append(f"[Document: {title}, Page {page}]\n{snippet}")
                else:
                    print(f"[CHAT]     WARNING: Empty snippet!")
            
            context = "\n\n".join(context_parts)
            print(f"[CHAT] Final context length: {len(context)} chars")
            if context:
                print(f"[CHAT] Context preview: {context[:200]}...")
            else:
                print(f"[CHAT] WARNING: Context is empty!")
            
            # Generate response using LLM
            print(f"[CHAT] Sending to Gemini LLM...")
            llm_start = time.time()
            response_text = llm_service.generate_response(query, context)
            llm_time = time.time() - llm_start
            print(f"[CHAT] LLM response received in {llm_time:.2f}s")
            print(f"[CHAT] Response length: {len(response_text)} chars")
            print(f"[CHAT] Response preview: {response_text[:100]}...")
            
            # Save assistant message
            print(f"[CHAT] Saving assistant message...")
            assistant_message = self.message_repo.create(
                conversation_id=conversation_id,
                role=RoleEnum.assistant,
                content=response_text
            )
            print(f"[CHAT] Assistant message saved (ID: {assistant_message.id})")
            
            # Update conversation title if first message
            msg_count = len(self.message_repo.get_by_conversation(conversation_id))
            print(f"[CHAT] Total messages in conversation: {msg_count}")
            if msg_count == 2:
                print(f"[CHAT] Updating conversation title from first message...")
                conversation.title = query[:50]
                self.conversation_repo.update(conversation)
            
            # Format citations for frontend
            print(f"[CHAT] Formatting {len(raw_citations)} citations for frontend...")
            formatted_citations = [
                {
                    "id": c.get('id', f"citation-{idx}"),
                    "documentId": c.get('documentId', ''),
                    "documentTitle": c.get('documentTitle', 'Unknown Document'),
                    "documentKind": c.get('documentKind', 'document'),
                    "page": c.get('page', 1),
                    "snippet": c.get('snippet', '')
                }
                for idx, c in enumerate(raw_citations[:5])
            ]
            
            total_time = time.time() - start_time
            print(f"[CHAT] Total processing time: {total_time:.2f}s")
            print(f"[CHAT] === MESSAGE COMPLETE ===\n")
            
            return {
                "message_id": assistant_message.id,
                "content": response_text,
                "citations": formatted_citations,
                "user_message_id": user_message.id
            }
            
        except Exception as e:
            print(f"[CHAT] ERROR in send_message: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    def get_conversation_messages(self, conversation_id: int, user_id: int) -> List:
        """Get all messages in a conversation"""
        print(f"[CHAT] Getting messages for conversation {conversation_id}")
        conversation = self.get_conversation(conversation_id, user_id)
        messages = self.message_repo.get_by_conversation(conversation_id)
        print(f"[CHAT] Found {len(messages)} messages")
        
        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
