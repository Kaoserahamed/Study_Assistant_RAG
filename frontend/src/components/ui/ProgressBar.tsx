interface ProgressBarProps {
  value: number
  tone?: 'ink' | 'highlighter' | 'mint'
}

const toneClasses = {
  ink: 'bg-ink',
  highlighter: 'bg-highlighter',
  mint: 'bg-mint',
}

export function ProgressBar({ value, tone = 'ink' }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div className="h-1.5 w-full rounded-full bg-ink/[0.08] overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-500 ease-out ${toneClasses[tone]}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
