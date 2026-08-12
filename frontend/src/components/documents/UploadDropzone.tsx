import { UploadCloud } from 'lucide-react'
import { type ChangeEvent, type DragEvent, useRef, useState } from 'react'

interface UploadDropzoneProps {
  onFiles: (files: File[]) => void
}

export function UploadDropzone({ onFiles }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length) onFiles(files)
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    if (files.length) onFiles(files)
    e.target.value = ''
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      className={`relative flex flex-col items-center justify-center text-center rounded-card border-2 border-dashed px-6 py-14 cursor-pointer transition-colors ${
        isDragging ? 'border-denim bg-denim/5' : 'border-paper-line bg-white hover:border-ink/25'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.ppt,.pptx,.doc,.docx,.txt"
        className="sr-only"
        onChange={handleChange}
      />
      <div className="h-12 w-12 rounded-full bg-highlighter-soft flex items-center justify-center mb-4">
        <UploadCloud className="h-5.5 w-5.5 text-highlighter-dark" strokeWidth={1.8} />
      </div>
      <p className="font-display text-lg text-ink mb-1">Drop files here, or click to browse</p>
      <p className="text-sm text-ink-soft max-w-sm">
        PDF textbooks, lecture notes, slide decks, and handouts. We'll index the pages so you can ask
        questions and get citations back to the exact source.
      </p>
      <p className="text-xs text-ink-faint mt-3">PDF, PPT, PPTX, DOCX, TXT · up to 100 MB each</p>
    </div>
  )
}
