import { FileStack, Trash2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import type { StudyDocument } from '@/types'
import { formatDate } from '@/utils/format'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { DocumentKindBadge } from './DocumentKindBadge'
import { StatusPill } from './StatusPill'
import { Modal } from '@/components/ui/Modal'
import { deleteDocument } from '@/services/api'

interface DocumentCardProps {
  doc: StudyDocument
  onDelete?: (docId: string) => void
}

export function DocumentCard({ doc, onDelete }: DocumentCardProps) {
  const navigate = useNavigate()
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const handleDelete = async () => {
    setIsDeleting(true)
    setDeleteError(null)
    try {
      await deleteDocument(doc.id)
      setShowDeleteModal(false)
      onDelete?.(doc.id)
      
      // Navigate back after deletion
      setTimeout(() => {
        navigate(-1)
      }, 300)
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : 'Failed to delete document')
    } finally {
      setIsDeleting(false)
    }
  }

  const content = (
    <Card className="group h-full flex flex-col gap-3 hover:border-ink/25 hover:shadow-tab transition-all relative">
      <div className="flex items-start justify-between gap-3">
        <div className={`h-10 w-10 rounded-md ${doc.thumbnailColor} flex items-center justify-center shrink-0`}>
          <FileStack className="h-4.5 w-4.5 text-white" strokeWidth={2} />
        </div>
        <div className="flex items-center gap-2">
          <StatusPill status={doc.status} />
          {doc.status === 'ready' && (
            <button
              onClick={(e) => {
                e.preventDefault()
                setShowDeleteModal(true)
              }}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 text-ink-faint hover:text-rust hover:bg-rust-soft rounded-md"
              title="Delete document"
            >
              <Trash2 className="h-4 w-4" strokeWidth={2} />
            </button>
          )}
        </div>
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
    return (
      <>
        <div className="cursor-default">{content}</div>
        <Modal
          isOpen={showDeleteModal}
          onClose={() => !isDeleting && setShowDeleteModal(false)}
          title="Delete Document"
        >
          <div className="space-y-4">
            <p className="text-sm text-ink-soft">
              Are you sure you want to delete <strong>{doc.title}</strong>? This action cannot be undone.
            </p>
            {deleteError && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
                {deleteError}
              </div>
            )}
            <div className="flex gap-3 justify-end pt-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
                className="px-4 py-2 rounded-lg border border-paper-line text-sm font-medium text-ink hover:bg-ink/[0.02] transition-colors disabled:opacity-60"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 rounded-lg bg-rust text-white text-sm font-medium hover:bg-rust/90 transition-colors disabled:opacity-60 flex items-center gap-2"
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </Modal>
      </>
    )
  }

  return (
    <>
      <Link to={`/library/${doc.id}`} className="block h-full">
        {content}
      </Link>
      <Modal
        isOpen={showDeleteModal}
        onClose={() => !isDeleting && setShowDeleteModal(false)}
        title="Delete Document"
      >
        <div className="space-y-4">
          <p className="text-sm text-ink-soft">
            Are you sure you want to delete <strong>{doc.title}</strong>? This action cannot be undone.
          </p>
          {deleteError && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
              {deleteError}
            </div>
          )}
          <div className="flex gap-3 justify-end pt-4">
            <button
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeleting}
              className="px-4 py-2 rounded-lg border border-paper-line text-sm font-medium text-ink hover:bg-ink/[0.02] transition-colors disabled:opacity-60"
            >
              Cancel
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-4 py-2 rounded-lg bg-rust text-white text-sm font-medium hover:bg-rust/90 transition-colors disabled:opacity-60 flex items-center gap-2"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  )
}
