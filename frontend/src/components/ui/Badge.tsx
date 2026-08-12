import type { HTMLAttributes } from 'react'

type Tone = 'neutral' | 'denim' | 'mint' | 'highlighter' | 'rust'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone
}

const toneClasses: Record<Tone, string> = {
  neutral: 'bg-ink/[0.06] text-ink-soft',
  denim: 'bg-denim/10 text-denim-dark',
  mint: 'bg-mint-soft text-mint-dark',
  highlighter: 'bg-highlighter-soft text-highlighter-dark',
  rust: 'bg-rust-soft text-rust',
}

export function Badge({ tone = 'neutral', className = '', children, ...props }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide ${toneClasses[tone]} ${className}`}
      {...props}
    >
      {children}
    </span>
  )
}
