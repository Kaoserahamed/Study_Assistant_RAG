import type { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padded?: boolean
}

export function Card({ padded = true, className = '', children, ...props }: CardProps) {
  return (
    <div
      className={`bg-white border border-paper-line rounded-card shadow-card ${padded ? 'p-5' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
