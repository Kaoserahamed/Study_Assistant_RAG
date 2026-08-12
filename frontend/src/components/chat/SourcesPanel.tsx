import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Citation } from '@/types'
import { DocumentKindBadge } from '@/components/documents/DocumentKindBadge'
import { EmptyState } from '@/components/ui/EmptyState'

interface SourcesPanelProps {
  citations: Citation[]
  activeCitationId?: string | null
}

export function SourcesPanel({ citations, activeCitationId }: SourcesPanelProps) {
  if (citations.length === 0) {
    return (
      <EmptyState
        icon={BookOpen}
        title="No sources yet"
        description="Ask a question and the passages it's grounded in will appear here, with links back to the exact page."
      />
    )
  }

  return (
    <div className="space-y-3">
      {citations.map((c, i) => (
        <Link
          key={c.id}
          to={`/library/${c.documentId}?page=${c.page}`}
          id={`source-${c.id}`}
          className={`block rounded-card border p-3.5 transition-colors ${
            activeCitationId === c.id
              ? 'border-highlighter-dark bg-highlighter-soft/60'
              : 'border-paper-line bg-white hover:border-ink/20'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-xs font-semibold text-ink-soft">[{i + 1}]</span>
            <DocumentKindBadge kind={c.documentKind} />
          </div>
          <p className="text-sm text-ink leading-relaxed mb-2">"{c.snippet}"</p>
          <p className="text-xs text-ink-faint truncate">
            {c.documentTitle} · page {c.page}
          </p>
        </Link>
      ))}
    </div>
  )
}
