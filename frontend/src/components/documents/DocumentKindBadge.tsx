import { BookOpen, FileText, NotebookPen, Presentation } from 'lucide-react'
import type { DocumentKind } from '@/types'
import { documentKindLabels } from '@/utils/format'

const kindConfig: Record<DocumentKind, { icon: typeof BookOpen; tone: string }> = {
  textbook: { icon: BookOpen, tone: 'text-denim' },
  'lecture-notes': { icon: NotebookPen, tone: 'text-mint-dark' },
  slides: { icon: Presentation, tone: 'text-highlighter-dark' },
  handout: { icon: FileText, tone: 'text-rust' },
}

export function DocumentKindBadge({ kind }: { kind: DocumentKind }) {
  const config = kindConfig[kind]
  
  // Fallback if kind is not recognized
  if (!config) {
    console.warn(`[DocumentKindBadge] Unknown document kind: ${kind}`)
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-denim">
        <BookOpen className="h-3.5 w-3.5" strokeWidth={2} />
        {documentKindLabels[kind] || 'Document'}
      </span>
    )
  }
  
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${config.tone}`}>
      <Icon className="h-3.5 w-3.5" strokeWidth={2} />
      {documentKindLabels[kind]}
    </span>
  )
}
