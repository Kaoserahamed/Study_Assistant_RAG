import { FileStack } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { StudyDocument } from '@/types'
import { formatDate } from '@/utils/format'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { DocumentKindBadge } from './DocumentKindBadge'
import { StatusPill } from './StatusPill'

export function DocumentCard({ doc }: { doc: StudyDocument }) {
  const content = (
    <Card className="group h-full flex flex-col gap-3 hover:border-ink/25 hover:shadow-tab transition-all">
      <div className="flex items-start justify-between gap-3">
        <div className={`h-10 w-10 rounded-md ${doc.thumbnailColor} flex items-center justify-center shrink-0`}>
          <FileStack className="h-4.5 w-4.5 text-white" strokeWidth={2} />
        </div>
        <StatusPill status={doc.status} />
      </div>

      <div className="flex-1">
        <p className="text-[11px] font-mono uppercase tracking-wide text-ink-faint mb-1">{doc.courseTag}</p>
        <h3 className="font-display text-base leading-snug text-ink mb-1.5 line-clamp-2">{doc.title}</h3>
        <p className="text-xs text-ink-soft leading-relaxed line-clamp-2">{doc.excerpt}</p>
      </div>

      {doc.status === 'processing' && typeof doc.progress === 'number' && (
        <ProgressBar value={doc.progress} tone="highlighter" />
      )}

      <div className="flex items-center justify-between pt-2 border-t border-paper-line text-xs text-ink-faint">
        <DocumentKindBadge kind={doc.kind} />
        <span>{doc.pageCount} pages · {doc.sizeLabel}</span>
      </div>
      <p className="text-[11px] text-ink-faint">Uploaded {formatDate(doc.uploadedAt)}</p>
    </Card>
  )

  if (doc.status !== 'ready') {
    return <div className="cursor-default">{content}</div>
  }

  return (
    <Link to={`/library/${doc.id}`} className="block h-full">
      {content}
    </Link>
  )
}
