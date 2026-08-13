import type { StudyDocument } from '@/types'
import { DocumentCard } from './DocumentCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'

interface DocumentGridProps {
  docs: StudyDocument[]
  onDocumentDelete?: (docId: string) => void
}

export function DocumentGrid({ docs, onDocumentDelete }: DocumentGridProps) {
  if (docs.length === 0) {
    return (
      <EmptyState
        icon={BookOpen}
        title="No materials here yet"
        description="Upload a textbook chapter, lecture notes, slides, or a handout to start building your library."
        action={
          <Link to="/upload">
            <Button size="sm">Upload materials</Button>
          </Link>
        }
      />
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {docs.map((doc) => (
        <DocumentCard 
          key={doc.id} 
          doc={doc} 
          onDelete={onDocumentDelete}
        />
      ))}
    </div>
  )
}
