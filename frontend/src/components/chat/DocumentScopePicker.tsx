import { Check } from 'lucide-react'
import type { StudyDocument } from '@/types'
import { DocumentKindBadge } from '@/components/documents/DocumentKindBadge'

interface DocumentScopePickerProps {
  documents: StudyDocument[]
  selectedIds: string[]
  onToggle: (id: string) => void
}

export function DocumentScopePicker({ documents, selectedIds, onToggle }: DocumentScopePickerProps) {
  const readyDocs = documents.filter((d) => d.status === 'ready')

  return (
    <div className="space-y-1">
      {readyDocs.map((doc) => {
        const checked = selectedIds.includes(doc.id)
        return (
          <button
            key={doc.id}
            onClick={() => onToggle(doc.id)}
            className={`w-full flex items-start gap-2.5 rounded-md px-2.5 py-2 text-left transition-colors ${
              checked ? 'bg-highlighter-soft/70' : 'hover:bg-ink/[0.04]'
            }`}
          >
            <span
              className={`mt-0.5 h-4 w-4 rounded shrink-0 flex items-center justify-center border transition-colors ${
                checked ? 'bg-ink border-ink' : 'border-ink/25 bg-white'
              }`}
            >
              {checked && <Check className="h-3 w-3 text-highlighter" strokeWidth={3} />}
            </span>
            <span className="min-w-0">
              <span className="block text-sm text-ink leading-snug truncate">{doc.title}</span>
              <span className="flex items-center gap-2 mt-0.5">
                <DocumentKindBadge kind={doc.kind} />
              </span>
            </span>
          </button>
        )
      })}
    </div>
  )
}
