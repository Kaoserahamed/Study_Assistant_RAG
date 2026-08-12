import { ArrowUp } from 'lucide-react'
import { type KeyboardEvent, useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'

interface ChatInputProps {
  onSend: (text: string) => void
  disabled?: boolean
  activeDocCount: number
}

export function ChatInput({ onSend, disabled, activeDocCount }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="border border-paper-line bg-white rounded-card p-2.5 shadow-card">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
          e.target.style.height = 'auto'
          e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`
        }}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your uploaded materials…"
        rows={1}
        className="w-full resize-none bg-transparent px-2 py-1.5 text-sm text-ink placeholder:text-ink-faint outline-none max-h-40"
      />
      <div className="flex items-center justify-between px-2 pt-1.5">
        <p className="text-[11px] text-ink-faint">
          Grounded in {activeDocCount} selected {activeDocCount === 1 ? 'document' : 'documents'}
        </p>
        <Button size="sm" onClick={submit} disabled={!value.trim() || disabled} className="!px-3">
          <ArrowUp className="h-3.5 w-3.5" />
          Ask
        </Button>
      </div>
    </div>
  )
}
