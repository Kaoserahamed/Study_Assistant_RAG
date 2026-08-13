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
from app.services.rag_context import build_context


class ChatService:
    def __init__(self, db: Session):
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.db = db

    @staticmethod
    def _build_context(citations: List[Dict[str, Any]], max_chars: int = None) -> str:
        return build_context(citations, max_chars)

    @staticmethod
    def _format_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return the stable citation contract stored with an assistant reply."""
        return [
            {
                "id": citation.get("id", f"citation-{index}"),
                "documentId": citation.get("documentId", ""),
                "documentTitle": citation.get("documentTitle", "Unknown Document"),
                "documentKind": citation.get("documentKind", "textbook"),
                "page": citation.get("page", 1),
                "snippet": citation.get("snippet", ""),
            }
            for index, citation in enumerate(citations)
        ]

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

    async def send_message_async(
        self,
        conversation_id: int,
        user_id: int,
        query: str,
        document_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response with citations (async)
        """
        print(f"\n[CHAT] === NEW MESSAGE (ASYNC) ===")
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
            raw_citations = await search_service.search_documents_async(query, user_id, document_ids=document_ids)
            search_time = time.time() - search_start
            print(f"[CHAT] Search completed in {search_time:.2f}s, found {len(raw_citations)} results")
            
            if raw_citations:
                for i, c in enumerate(raw_citations[:2]):
                    print(f"[CHAT]   Result {i+1}: {c.get('documentTitle', 'N/A')} page {c.get('page', 'N/A')}")
            
            # Build context from citations
            print(f"[CHAT] Building context from {len(raw_citations)} citations...")
            context = self._build_context(raw_citations)
            print(f"[CHAT] Final context length: {len(context)} chars")
            if context:
                print(f"[CHAT] Context preview: {context[:200]}...")
            else:
                print(f"[CHAT] WARNING: Context is empty!")
            
            # Generate response using LLM (async)
            print(f"[CHAT] Sending to Gemini LLM (async)...")
            llm_start = time.time()
            response_text = await llm_service.generate_response_async(query, context)
            llm_time = time.time() - llm_start
            print(f"[CHAT] LLM response received in {llm_time:.2f}s")
            print(f"[CHAT] Response length: {len(response_text)} chars")
            print(f"[CHAT] Response preview: {response_text[:100]}...")
            
            # Format citations once, then persist exactly what the frontend sees.
            formatted_citations = self._format_citations(raw_citations)

            # Save assistant message
            print(f"[CHAT] Saving assistant message...")
            assistant_message = self.message_repo.create(
                conversation_id=conversation_id,
                role=RoleEnum.assistant,
                content=response_text,
                citations=formatted_citations,
            )
            print(f"[CHAT] Assistant message saved (ID: {assistant_message.id})")
            
            # Update conversation title if first message
            msg_count = len(self.message_repo.get_by_conversation(conversation_id))
            print(f"[CHAT] Total messages in conversation: {msg_count}")
            if msg_count == 2:
                print(f"[CHAT] Updating conversation title from first message...")
                conversation.title = query[:50]
                self.conversation_repo.update(conversation)
            
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
            print(f"[CHAT] ERROR in send_message_async: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

    def send_message(
        self,
        conversation_id: int,
        user_id: int,
        query: str,
        document_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response with citations (sync wrapper, deprecated)
        
        Use send_message_async in async contexts instead.
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
            context = self._build_context(raw_citations)
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
            
            formatted_citations = self._format_citations(raw_citations)

            # Save assistant message
            print(f"[CHAT] Saving assistant message...")
            assistant_message = self.message_repo.create(
                conversation_id=conversation_id,
                role=RoleEnum.assistant,
                content=response_text,
                citations=formatted_citations,
            )
            print(f"[CHAT] Assistant message saved (ID: {assistant_message.id})")
            
            # Update conversation title if first message
            msg_count = len(self.message_repo.get_by_conversation(conversation_id))
            print(f"[CHAT] Total messages in conversation: {msg_count}")
            if msg_count == 2:
                print(f"[CHAT] Updating conversation title from first message...")
                conversation.title = query[:50]
                self.conversation_repo.update(conversation)
            
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
                "created_at": msg.created_at.isoformat(),
                "citations": msg.citations or [],
            }
            for msg in messages
        ]
