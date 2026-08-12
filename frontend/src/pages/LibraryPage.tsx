import { Search, UploadCloud } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { DocumentGrid } from '@/components/documents/DocumentGrid'
import { KindFilterBar } from '@/components/documents/KindFilterBar'
import { useDocuments } from '@/hooks/useDocuments'
import type { DocumentKind } from '@/types'

export function LibraryPage() {
  const { documents, isLoading } = useDocuments()
  const [activeKind, setActiveKind] = useState<DocumentKind | 'all'>('all')
  const [query, setQuery] = useState('')

  const counts = useMemo(() => {
    const base: Record<string, number> = { all: documents.length }
    documents.forEach((d) => {
      base[d.kind] = (base[d.kind] ?? 0) + 1
    })
    return base
  }, [documents])

  const filtered = documents.filter((d) => {
    const matchesKind = activeKind === 'all' || d.kind === activeKind
    const matchesQuery =
      query.trim() === '' ||
      d.title.toLowerCase().includes(query.toLowerCase()) ||
      d.courseTag.toLowerCase().includes(query.toLowerCase())
    return matchesKind && matchesQuery
  })

  return (
    <div className="max-w-6xl mx-auto px-6 md:px-10 py-8 md:py-10">
      <PageHeader
        eyebrow={`${documents.length} materials`}
        title="Your library"
        description="Everything you've uploaded, organized by course and type. Open any ready document to read it with cited passages highlighted."
        action={
          <Link to="/upload">
            <Button size="md">
              <UploadCloud className="h-4 w-4" />
              Upload more
            </Button>
          </Link>
        }
      />

      <div className="flex flex-col md:flex-row md:items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by title or course…"
            className="w-full rounded-md border border-paper-line bg-white pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-denim outline-none transition-colors"
          />
        </div>
        <KindFilterBar active={activeKind} onChange={setActiveKind} counts={counts} />
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-44 rounded-card bg-white border border-paper-line animate-pulse" />
          ))}
        </div>
      ) : (
        <DocumentGrid docs={filtered} />
      )}
    </div>
  )
}
