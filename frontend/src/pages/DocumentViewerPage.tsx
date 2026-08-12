import { ArrowLeft, ChevronLeft, ChevronRight, MessageSquare } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { DocumentKindBadge } from '@/components/documents/DocumentKindBadge'
import { useDocuments } from '@/hooks/useDocuments'

export function DocumentViewerPage() {
  const { docId } = useParams()
  const [searchParams] = useSearchParams()
  const { documents, isLoading } = useDocuments()
  const doc = documents.find((d) => d.id === docId)

  const targetPage = Number(searchParams.get('page') ?? 1)
  const [page, setPage] = useState(targetPage || 1)

  useEffect(() => {
    if (targetPage) setPage(targetPage)
  }, [targetPage])

  if (isLoading) {
    return <div className="max-w-4xl mx-auto px-6 py-10 text-sm text-ink-soft">Loading document…</div>
  }

  if (!doc) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <p className="text-sm text-ink-soft mb-3">We couldn't find that document.</p>
        <Link to="/library" className="text-sm text-denim hover:underline">
          Back to library
        </Link>
      </div>
    )
  }

  const isCitedPage = page === targetPage

  return (
    <div className="max-w-4xl mx-auto px-6 md:px-10 py-8">
      <Link to="/library" className="inline-flex items-center gap-1.5 text-xs text-ink-soft hover:text-ink mb-6">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to library
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <DocumentKindBadge kind={doc.kind} />
          <h1 className="font-display text-2xl text-ink mt-1.5">{doc.title}</h1>
          <p className="text-xs text-ink-faint mt-1">
            {doc.courseTag} · {doc.pageCount} pages
          </p>
        </div>
        <Link to={`/chat?docs=${doc.id}`}>
          <Button variant="secondary" size="sm">
            <MessageSquare className="h-3.5 w-3.5" />
            Ask about this document
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-paper-line rounded-card shadow-card overflow-hidden">
        <div
          className={`aspect-[8.5/11] p-10 md:p-14 relative transition-colors ${
            isCitedPage ? 'bg-highlighter-soft/30' : ''
          }`}
        >
          {isCitedPage && (
            <div className="absolute top-4 right-4 text-[11px] font-mono uppercase tracking-wide text-highlighter-dark bg-highlighter-soft rounded-full px-2.5 py-1">
              Cited passage
            </div>
          )}
          <p className="text-[11px] font-mono text-ink-faint mb-6">
            {doc.title} — page {page}
          </p>
          <div className="space-y-4">
            <div className={`h-4 w-3/4 rounded ${isCitedPage ? 'bg-highlighter/50' : 'bg-ink/[0.08]'}`} />
            <div className="h-3 w-full rounded bg-ink/[0.06]" />
            <div className="h-3 w-full rounded bg-ink/[0.06]" />
            <div className={`h-3 w-11/12 rounded ${isCitedPage ? 'bg-highlighter/50' : 'bg-ink/[0.06]'}`} />
            <div className={`h-3 w-5/6 rounded ${isCitedPage ? 'bg-highlighter/50' : 'bg-ink/[0.06]'}`} />
            <div className="h-3 w-full rounded bg-ink/[0.06]" />
            <div className="h-3 w-2/3 rounded bg-ink/[0.06]" />
            <div className="pt-2" />
            <div className="h-3 w-full rounded bg-ink/[0.06]" />
            <div className="h-3 w-full rounded bg-ink/[0.06]" />
            <div className="h-3 w-4/5 rounded bg-ink/[0.06]" />
          </div>
          {isCitedPage && (
            <p className="mt-6 text-sm text-ink-soft italic leading-relaxed border-l-2 border-highlighter-dark pl-3">
              This is a preview render — in the full product, the exact cited sentences on this page are
              highlighted in place, matching the excerpt shown in your chat sources panel.
            </p>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-paper-line px-5 py-3 bg-paper">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Prev
          </Button>
          <span className="text-xs text-ink-faint font-mono">
            Page {page} of {doc.pageCount}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage((p) => Math.min(doc.pageCount, p + 1))}
            disabled={page >= doc.pageCount}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
