import { GraduationCap, Sparkles } from 'lucide-react'
import type { ChatMessage, Citation } from '@/types'
import { formatTime } from '@/utils/format'
import { CitationTab } from './CitationTab'

interface ChatBubbleProps {
  message: ChatMessage
  onSelectCitation: (citation: Citation) => void
  activeCitationId?: string | null
}

export function ChatBubble({ message, onSelectCitation, activeCitationId }: ChatBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-denim text-white' : 'bg-ink text-highlighter'
        }`}
      >
        {isUser ? <GraduationCap className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
      </div>

      <div className={`flex flex-col gap-2 max-w-[42rem] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-card px-4 py-3 text-sm leading-relaxed whitespace-pre-line ${
            isUser ? 'bg-denim text-white rounded-tr-sm' : 'bg-white border border-paper-line rounded-tl-sm'
          }`}
        >
          {message.content}
          {message.isStreaming && (
            <span className="inline-flex gap-1 ml-1 align-middle">
              <span className="h-1.5 w-1.5 rounded-full bg-ink-faint animate-pulse-dot" />
              <span className="h-1.5 w-1.5 rounded-full bg-ink-faint animate-pulse-dot [animation-delay:0.15s]" />
              <span className="h-1.5 w-1.5 rounded-full bg-ink-faint animate-pulse-dot [animation-delay:0.3s]" />
            </span>
          )}
        </div>

        {message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.citations.map((c, i) => (
              <CitationTab
                key={c.id}
                citation={c}
                index={i + 1}
                onSelect={onSelectCitation}
                isActive={activeCitationId === c.id}
              />
            ))}
          </div>
        )}

        <span className="text-[11px] text-ink-faint px-0.5">{formatTime(message.createdAt)}</span>
      </div>
    </div>
  )
}
