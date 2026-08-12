import type { LucideIcon } from 'lucide-react'
import { Card } from '@/components/ui/Card'

interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string
  tone: string
}

export function StatCard({ icon: Icon, label, value, tone }: StatCardProps) {
  return (
    <Card className="flex items-center gap-3.5">
      <div className={`h-10 w-10 rounded-md flex items-center justify-center shrink-0 ${tone}`}>
        <Icon className="h-4.5 w-4.5 text-white" strokeWidth={2} />
      </div>
      <div>
        <p className="font-display text-2xl leading-none text-ink">{value}</p>
        <p className="text-xs text-ink-soft mt-1">{label}</p>
      </div>
    </Card>
  )
}
