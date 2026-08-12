import type { Citation } from '@/types'

interface CitationTabProps {
  citation: Citation
  index: number
  onSelect: (citation: Citation) => void
  isActive?: boolean
}

export function CitationTab({ citation, index, onSelect, isActive }: CitationTabProps) {
  return (
    <button
      onClick={() => onSelect(citation)}
      className={`group inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-mono transition-all shrink-0 ${
        isActive
          ? 'bg-highlighter border-highlighter-dark text-ink shadow-tab'
          : 'bg-highlighter-soft border-transparent text-highlighter-dark hover:bg-highlighter hover:shadow-tab'
      }`}
      title={`${citation.documentTitle}, p. ${citation.page}`}
    >
      <span className="font-semibold">[{index}]</span>
      <span className="hidden sm:inline truncate max-w-[9rem]">{citation.documentTitle}</span>
      <span className="text-ink-faint group-hover:text-ink/70">p.{citation.page}</span>
    </button>
  )
}
