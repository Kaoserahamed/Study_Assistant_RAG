import type { DocumentKind } from '@/types'
import { documentKindLabels } from '@/utils/format'

interface KindFilterBarProps {
  active: DocumentKind | 'all'
  onChange: (kind: DocumentKind | 'all') => void
  counts: Record<string, number>
}

const kinds: (DocumentKind | 'all')[] = ['all', 'textbook', 'lecture-notes', 'slides', 'handout']

export function KindFilterBar({ active, onChange, counts }: KindFilterBarProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {kinds.map((kind) => {
        const label = kind === 'all' ? 'All materials' : documentKindLabels[kind]
        const isActive = active === kind
        return (
          <button
            key={kind}
            onClick={() => onChange(kind)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium border transition-colors ${
              isActive
                ? 'bg-ink text-paper border-ink'
                : 'bg-white text-ink-soft border-paper-line hover:border-ink/30'
            }`}
          >
            {label}
            <span className={`ml-1.5 ${isActive ? 'text-paper/60' : 'text-ink-faint'}`}>{counts[kind] ?? 0}</span>
          </button>
        )
      })}
    </div>
  )
}
