import { CheckCircle2, Clock, Loader2, XCircle } from 'lucide-react'
import type { DocumentStatus } from '@/types'

const config: Record<DocumentStatus, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  ready: { label: 'Ready to ask', className: 'text-mint-dark bg-mint-soft', icon: CheckCircle2 },
  processing: { label: 'Processing', className: 'text-denim bg-denim/10', icon: Loader2 },
  queued: { label: 'Queued', className: 'text-ink-soft bg-ink/[0.06]', icon: Clock },
  failed: { label: 'Failed', className: 'text-rust bg-rust-soft', icon: XCircle },
}

export function StatusPill({ status }: { status: DocumentStatus }) {
  const { label, className, icon: Icon } = config[status]
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${className}`}>
      <Icon className={`h-3 w-3 ${status === 'processing' ? 'animate-spin' : ''}`} strokeWidth={2.2} />
      {label}
    </span>
  )
}
