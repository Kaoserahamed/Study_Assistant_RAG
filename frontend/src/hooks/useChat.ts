import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ChatMessage, Citation } from '@/types'
import { sendMessage, createConversation, getConversation } from '@/services/api'

export function useChat(initialMessages: ChatMessage[] = []) {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [isAsking, setIsAsking] = useState(false)
  const [conversationId, setConversationId] = useState<number | null>(null)

  const loadConversation = useCallback(async (convId: number) => {
    try {
      console.log('[useChat] Loading conversation:', convId)
      const conversation = await getConversation(convId)
      
      // Convert backend messages to ChatMessage format
      const loadedMessages: ChatMessage[] = conversation.messages.map((msg: any) => ({
        id: `msg-${msg.id}`,
        role: msg.role,
        content: msg.content,
        citations: msg.citations || [],
        createdAt: msg.created_at,
      }))
      
      console.log('[useChat] Loaded', loadedMessages.length, 'messages')
      setMessages(loadedMessages)
      setConversationId(convId)
    } catch (error) {
      console.error('[useChat] Failed to load conversation:', error)
    }
  }, [])

  const send = useCallback(async (question: string, documentIds: string[]) => {
    try {
      // Create conversation if it doesn't exist
      let convId: number | null = conversationId
      if (!convId) {
        try {
          const conversation = await createConversation(question.substring(0, 50))
          convId = conversation.id
          setConversationId(conversation.id)
          // Navigate to conversation URL for persistence on refresh
          navigate(`/chat/${conversation.id}`)
        } catch (error) {
          console.error('Failed to create conversation:', error)
          throw error
        }
      }

      if (!convId) {
        throw new Error('Could not create conversation')
      }

      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: question,
        createdAt: new Date().toISOString(),
      }
      const pendingId = `msg-${Date.now()}-a`
      const pendingMessage: ChatMessage = {
        id: pendingId,
        role: 'assistant',
        content: 'Reading through your selected materials…',
        createdAt: new Date().toISOString(),
        isStreaming: true,
      }
      setMessages((prev) => [...prev, userMessage, pendingMessage])
      setIsAsking(true)

      // Convert documentIds from 'doc-123' format to just '123'
      const docIds = documentIds.map(id => id.replace('doc-', ''))
      
      try {
        const result = await sendMessage(convId, question, docIds)
        
        // Ensure citations is an array
        const citations = Array.isArray(result.citations) ? result.citations : []
        
        setMessages((prev) =>
          prev.map((m) =>
            m.id === pendingId
              ? { ...m, content: result.content, citations, isStreaming: false }
              : m,
          ),
        )
      } catch (error) {
        console.error('Failed to send message:', error)
        // Update pending message with error
        setMessages((prev) =>
          prev.map((m) =>
            m.id === pendingId
              ? { 
                  ...m, 
                  content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
                  isStreaming: false 
                }
              : m,
          ),
        )
      }
    } finally {
      setIsAsking(false)
    }
  }, [conversationId, navigate])

  const lastActiveCitation = useCallback((): Citation | null => {
    const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant' && m.citations?.length)
    return lastAssistant?.citations?.[0] ?? null
  }, [messages])

  return { messages, isAsking, send, lastActiveCitation, loadConversation }
}
