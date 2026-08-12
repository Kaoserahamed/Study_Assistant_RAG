import type { DocumentKind } from '@/types'

export function formatDate(iso: string): string {
  const date = new Date(iso)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatTime(iso: string): string {
  const date = new Date(iso)
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

export const documentKindLabels: Record<DocumentKind, string> = {
  textbook: 'Textbook',
  'lecture-notes': 'Lecture notes',
  slides: 'Slides',
  handout: 'Handout',
}

export function inferKindFromFileName(fileName: string): DocumentKind {
  const lower = fileName.toLowerCase()
  if (lower.includes('slide') || lower.endsWith('.ppt') || lower.endsWith('.pptx')) return 'slides'
  if (lower.includes('note')) return 'lecture-notes'
  if (lower.includes('handout') || lower.includes('worksheet') || lower.includes('problem')) return 'handout'
  return 'textbook'
}

export function bytesToLabel(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
