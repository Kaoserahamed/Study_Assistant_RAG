import { CheckCircle2, FileText } from 'lucide-react'
import type { UploadTask } from '@/types'
import { ProgressBar } from '@/components/ui/ProgressBar'

export function UploadTaskRow({ task }: { task: UploadTask }) {
  const isDone = task.status === 'ready' || task.status === 'processing'
  return (
    <div className="flex items-center gap-3 py-3 border-b border-paper-line last:border-b-0">
      <div className="h-8 w-8 rounded-md bg-ink/[0.05] flex items-center justify-center shrink-0">
        <FileText className="h-4 w-4 text-ink-soft" strokeWidth={1.8} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="text-sm text-ink truncate">{task.fileName}</p>
          <span className="text-xs text-ink-faint shrink-0">{task.sizeLabel}</span>
        </div>
        {task.progress < 100 ? (
          <ProgressBar value={task.progress} tone="highlighter" />
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-mint-dark">
            <CheckCircle2 className="h-3.5 w-3.5" />
            {isDone ? 'Uploaded — queued for indexing' : 'Uploaded'}
          </div>
        )}
      </div>
    </div>
  )
}
