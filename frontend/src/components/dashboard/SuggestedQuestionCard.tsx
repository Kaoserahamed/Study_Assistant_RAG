import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export function SuggestedQuestionCard({ question }: { question: string }) {
  return (
    <Link
      to={`/chat?q=${encodeURIComponent(question)}`}
      className="group flex items-center justify-between gap-3 rounded-card border border-paper-line bg-white px-4 py-3.5 hover:border-denim/40 hover:bg-denim/[0.03] transition-colors"
    >
      <span className="text-sm text-ink leading-snug">{question}</span>
      <ArrowUpRight className="h-4 w-4 text-ink-faint group-hover:text-denim shrink-0 transition-colors" />
    </Link>
  )
}
