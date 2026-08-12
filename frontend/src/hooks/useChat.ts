import { useCallback, useState } from 'react'
import type { ChatMessage, Citation } from '@/types'
import { askQuestion } from '@/services/api'

export function useChat(initialMessages: ChatMessage[] = []) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [isAsking, setIsAsking] = useState(false)

  const send = useCallback(async (question: string, documentIds: string[]) => {
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

    try {
      const result = await askQuestion(question, documentIds)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { ...m, content: result.content, citations: result.citations, isStreaming: false }
            : m,
        ),
      )
    } finally {
      setIsAsking(false)
    }
  }, [])

  const lastActiveCitation = useCallback((): Citation | null => {
    const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant' && m.citations?.length)
    return lastAssistant?.citations?.[0] ?? null
  }, [messages])

  return { messages, isAsking, send, lastActiveCitation }
}
