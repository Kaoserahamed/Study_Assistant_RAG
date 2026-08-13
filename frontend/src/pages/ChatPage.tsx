import { BookOpen, PanelRightOpen, Sparkles } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { ChatBubble } from '@/components/chat/ChatBubble'
import { ChatInput } from '@/components/chat/ChatInput'
import { DocumentScopePicker } from '@/components/chat/DocumentScopePicker'
import { SourcesPanel } from '@/components/chat/SourcesPanel'
import { Button } from '@/components/ui/Button'
import { useChat } from '@/hooks/useChat'
import { useDocuments } from '@/hooks/useDocuments'
import type { Citation } from '@/types'

export function ChatPage() {
  const { conversationId } = useParams()
  const { documents, isLoading } = useDocuments()
  const [searchParams] = useSearchParams()
  const { messages, isAsking, send, loadConversation } = useChat([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null)
  const [showSourcesMobile, setShowSourcesMobile] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const initializedFromQuery = useRef(false)

  // Load existing conversation if conversationId is provided
  useEffect(() => {
    if (conversationId) {
      console.log('[ChatPage] Loading conversation:', conversationId)
      loadConversation(parseInt(conversationId))
    }
  }, [conversationId, loadConversation])

  useEffect(() => {
    if (documents.length && selectedDocIds.length === 0) {
      const preselected = searchParams.get('docs')
      setSelectedDocIds(
        preselected ? preselected.split(',') : documents.filter((d) => d.status === 'ready').map((d) => d.id),
      )
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documents])

  useEffect(() => {
    const q = searchParams.get('q')
    if (q && !initializedFromQuery.current) {
      initializedFromQuery.current = true
      send(q, selectedDocIds)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, selectedDocIds])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const allCitations = useMemo(() => {
    const map = new Map<string, Citation>()
    messages.forEach((m) => m.citations?.forEach((c) => map.set(c.id, c)))
    return Array.from(map.values())
  }, [messages])

  const toggleDoc = (id: string) => {
    setSelectedDocIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  return (
    <div className="flex h-screen">
      {/* Document scope column */}
      <div className="hidden lg:flex w-64 shrink-0 flex-col border-r border-paper-line bg-paper">
        <div className="px-4 pt-6 pb-3">
          <p className="text-xs font-mono uppercase tracking-widest text-ink-faint mb-1">Scope</p>
          <h2 className="font-display text-lg text-ink">Materials to search</h2>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-4">
          {isLoading ? (
            <p className="px-2.5 text-sm text-ink-faint">Loading…</p>
          ) : (
            <DocumentScopePicker documents={documents} selectedIds={selectedDocIds} onToggle={toggleDoc} />
          )}
        </div>
      </div>

      {/* Chat column */}
      <div className="flex-1 min-w-0 flex flex-col">
        <div className="flex items-center justify-between border-b border-paper-line px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-full bg-ink flex items-center justify-center">
              <Sparkles className="h-3.5 w-3.5 text-highlighter" />
            </div>
            <div>
              <p className="text-sm font-medium text-ink leading-none">Study assistant</p>
              <p className="text-[11px] text-ink-faint mt-0.5">
                {selectedDocIds.length} {selectedDocIds.length === 1 ? 'source' : 'sources'} selected
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setShowSourcesMobile(true)}>
            <PanelRightOpen className="h-4 w-4" />
            Sources
          </Button>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin px-6 py-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto">
              <div className="h-11 w-11 rounded-full bg-highlighter-soft flex items-center justify-center mb-4">
                <BookOpen className="h-5 w-5 text-highlighter-dark" />
              </div>
              <h3 className="font-display text-lg text-ink mb-1.5">Ask about your course materials</h3>
              <p className="text-sm text-ink-soft">
                Questions are answered using only the documents you've selected, with citations back to the
                exact page.
              </p>
            </div>
          ) : (
            messages.map((m) => (
              <ChatBubble
                key={m.id}
                message={m}
                onSelectCitation={setActiveCitation}
                activeCitationId={activeCitation?.id}
              />
            ))
          )}
        </div>

        <div className="px-6 pb-6 pt-2">
          <ChatInput
            onSend={(text) => send(text, selectedDocIds)}
            disabled={isAsking}
            activeDocCount={selectedDocIds.length}
          />
        </div>
      </div>

      {/* Sources column */}
      <div className="hidden xl:flex w-80 shrink-0 flex-col border-l border-paper-line bg-paper">
        <div className="px-4 pt-6 pb-3">
          <p className="text-xs font-mono uppercase tracking-widest text-ink-faint mb-1">Grounded in</p>
          <h2 className="font-display text-lg text-ink">Sources</h2>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin px-4 pb-6">
          <SourcesPanel citations={allCitations} activeCitationId={activeCitation?.id} />
        </div>
      </div>

      {/* Mobile sources drawer */}
      {showSourcesMobile && (
        <div className="fixed inset-0 z-50 xl:hidden">
          <div className="absolute inset-0 bg-ink/40" onClick={() => setShowSourcesMobile(false)} />
          <div className="absolute right-0 top-0 bottom-0 w-80 max-w-[85vw] bg-paper border-l border-paper-line p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-lg text-ink">Sources</h2>
              <Button variant="ghost" size="sm" onClick={() => setShowSourcesMobile(false)}>
                Close
              </Button>
            </div>
            <SourcesPanel citations={allCitations} activeCitationId={activeCitation?.id} />
          </div>
        </div>
      )}
    </div>
  )
}
