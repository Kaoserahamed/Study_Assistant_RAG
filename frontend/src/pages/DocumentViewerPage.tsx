import { ArrowLeft, ChevronLeft, ChevronRight, MessageSquare, Loader, AlertCircle } from 'lucide-react'
import React, { useEffect, useState, useRef, useCallback } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import * as pdfjsLib from 'pdfjs-dist'
import { Button } from '@/components/ui/Button'
import { DocumentKindBadge } from '@/components/documents/DocumentKindBadge'
import { useDocuments } from '@/hooks/useDocuments'
import { getDocumentFileUrl } from '@/services/api'

// Set up PDF.js worker - use local copy from public directory
pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js'

console.log('[PDF] Initialized with worker:', pdfjsLib.GlobalWorkerOptions.workerSrc)

export function DocumentViewerPage() {
  const { docId } = useParams()
  const [searchParams] = useSearchParams()
  const { documents, isLoading } = useDocuments()
  const doc = documents.find((d) => d.id === docId)

  const targetPage = Number(searchParams.get('page') ?? 1)
  const [page, setPage] = useState(targetPage || 1)
  const [numPages, setNumPages] = useState<number | null>(null)
  const [isLoadingPdf, setIsLoadingPdf] = useState(true)
  const [pdfUrl, setPdfUrl] = useState<string>('')
  const [textContent, setTextContent] = useState<string>('')
  const [isPdfFile, setIsPdfFile] = useState(false)
  const [error, setError] = useState<string>('')

  // Memoize the callback to prevent unnecessary re-renders of PdfCanvas
  const handlePagesLoaded = useCallback((n: number) => {
    console.log('[DocumentViewerPage] Pages loaded:', n)
    setNumPages(n)
    setIsLoadingPdf(false)
  }, [])

  useEffect(() => {
    if (targetPage) setPage(targetPage)
  }, [targetPage])

  // Fetch document (PDF or text) with proper authentication
  useEffect(() => {
    if (!doc) return
    let objectUrl: string | null = null

    const fetchDocument = async () => {
      try {
        setIsLoadingPdf(true)
        setError('')
        setIsPdfFile(false)
        setPdfUrl('')
        setTextContent('')
        
        const token = localStorage.getItem('access_token')
        const fileUrl = getDocumentFileUrl(doc.id)
        
        console.log('Fetching document from:', fileUrl)
        
        const response = await fetch(fileUrl, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const blob = await response.blob()
        console.log('Document blob received, size:', blob.size, 'type:', blob.type)
        
        // Check if it's a PDF or text file based on MIME type and filename
        const fileName = doc.title.toLowerCase()
        const isBlobPdf = blob.type === 'application/pdf' || fileName.endsWith('.pdf')
        const isTextFile = blob.type.startsWith('text/') || fileName.endsWith('.txt')
        
        if (isBlobPdf) {
          console.log('Detected as PDF file, creating blob URL...')
          const url = URL.createObjectURL(blob)
          objectUrl = url
          console.log('PDF Object URL created:', url)
          setPdfUrl(url)
          setIsPdfFile(true)
          setIsLoadingPdf(false)  // Allow PdfCanvas to render now
        } else if (isTextFile) {
          // It's a text file - read as text
          console.log('Detected as text file, reading content...')
          const text = await blob.text()
          console.log('Text content read, length:', text.length)
          setTextContent(text)
          setIsPdfFile(false)
          // For text files, assume 1 page
          setNumPages(1)
          setIsLoadingPdf(false)
        } else {
          setError('Preview is currently available for PDF and text documents. You can still use this document in chat.')
          setIsLoadingPdf(false)
        }
      } catch (err) {
        console.error('Error fetching document:', err)
        setError(err instanceof Error ? err.message : 'Failed to load document')
        setIsLoadingPdf(false)
      }
    }

    fetchDocument()

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [doc?.id, doc?.title])

  if (isLoading) {
    return <div className="max-w-4xl mx-auto px-6 py-10 text-sm text-ink-soft">Loading document…</div>
  }

  if (!doc) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <p className="text-sm text-ink-soft mb-3">We couldn't find that document.</p>
        <Link to="/library" className="text-sm text-denim hover:underline">
          Back to library
        </Link>
      </div>
    )
  }

  const isCitedPage = page === targetPage

  return (
    <div className="max-w-4xl mx-auto px-6 md:px-10 py-8">
      <Link to="/library" className="inline-flex items-center gap-1.5 text-xs text-ink-soft hover:text-ink mb-6">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to library
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <DocumentKindBadge kind={doc.kind} />
          <h1 className="font-display text-2xl text-ink mt-1.5">{doc.title}</h1>
          <p className="text-xs text-ink-faint mt-1">
            {doc.courseTag} · {doc.pageCount} pages
          </p>
        </div>
        <Link to={`/chat?docs=${doc.id}`}>
          <Button variant="secondary" size="sm">
            <MessageSquare className="h-3.5 w-3.5" />
            Ask about this document
          </Button>
        </Link>
      </div>

      <div className="bg-white border border-paper-line rounded-card shadow-card overflow-hidden">
        <div className={`aspect-[8.5/11] p-4 md:p-6 relative transition-colors flex flex-col items-center justify-center overflow-auto ${
          isCitedPage ? 'bg-highlighter-soft/30' : ''
        }`}>
          {isCitedPage && (
            <div className="absolute top-4 right-4 text-[11px] font-mono uppercase tracking-wide text-highlighter-dark bg-highlighter-soft rounded-full px-2.5 py-1 z-10">
              Cited passage
            </div>
          )}
          
          {error ? (
            <div className="flex flex-col items-center justify-center gap-2 text-red-600">
              <AlertCircle className="h-6 w-6" />
              <p className="text-sm">{error}</p>
            </div>
          ) : isLoadingPdf ? (
            <div className="flex flex-col items-center justify-center gap-2">
              <Loader className="h-6 w-6 animate-spin text-ink-soft" />
              <p className="text-sm text-ink-soft">Loading document…</p>
            </div>
          ) : isPdfFile && pdfUrl ? (
            <PdfCanvas url={pdfUrl} pageNum={page} onPagesLoaded={handlePagesLoaded} />
          ) : !isPdfFile && textContent ? (
            <div className="w-full h-full whitespace-pre-wrap text-sm text-ink leading-relaxed overflow-auto font-mono">
              {textContent}
            </div>
          ) : null}
        </div>

        <div className="flex items-center justify-between border-t border-paper-line px-5 py-3 bg-paper">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1 || !isPdfFile}
          >
            <ChevronLeft className="h-4 w-4" />
            Prev
          </Button>
          <span className="text-xs text-ink-faint font-mono">
            Page {page} of {numPages || doc.pageCount}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setPage((p) => Math.min(numPages || doc.pageCount, p + 1))}
            disabled={page >= (numPages || doc.pageCount) || !isPdfFile}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

// PDF Canvas component that renders PDF directly using pdf.js
// Wrapped in React.memo to prevent unnecessary re-renders
const PdfCanvas = React.memo(function PdfCanvasImpl({ url, pageNum, onPagesLoaded }: { url: string; pageNum: number; onPagesLoaded: (n: number) => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const renderTaskRef = useRef<any>(null)
  const abortControllerRef = useRef(new AbortController())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    console.log('[PdfCanvas] useEffect triggered, url:', url, 'pageNum:', pageNum, 'canvasRef:', !!canvasRef.current)
    
    if (!url) {
      console.log('[PdfCanvas] No URL provided')
      return
    }

    if (!canvasRef.current) {
      console.log('[PdfCanvas] Canvas ref not available')
      return
    }

    // Create a new abort controller for this effect run
    const abortController = new AbortController()
    abortControllerRef.current = abortController

    const renderPdf = async () => {
      try {
        // Cancel any previous render operation
        if (renderTaskRef.current) {
          console.log('[PdfCanvas] Cancelling previous render task')
          renderTaskRef.current.cancel()
          renderTaskRef.current = null
        }

        setLoading(true)
        setError(null)
        console.log('[PdfCanvas] Starting PDF load from:', url)

        // Load PDF
        console.log('[PdfCanvas] Calling pdfjsLib.getDocument()')
        const pdfPromise = pdfjsLib.getDocument(url)
        console.log('[PdfCanvas] Got promise, awaiting...')
        const pdfDoc = await pdfPromise.promise
        
        // Check if this effect was aborted
        if (abortController.signal.aborted) {
          console.log('[PdfCanvas] Effect was aborted, stopping render')
          return
        }

        console.log('[PdfCanvas] PDF loaded successfully! Pages:', pdfDoc.numPages)
        onPagesLoaded(pdfDoc.numPages)

        // Render specific page
        const pageNumber = Math.min(pageNum, pdfDoc.numPages)
        console.log('[PdfCanvas] Getting page:', pageNumber)
        const page = await pdfDoc.getPage(pageNumber)
        console.log('[PdfCanvas] Page object obtained, rendering...')

        const viewport = page.getViewport({ scale: 1.5 })
        console.log('[PdfCanvas] Viewport size:', viewport.width, 'x', viewport.height)
        
        const canvas = canvasRef.current
        
        // Check if canvas still exists
        if (!canvas) {
          console.log('[PdfCanvas] Canvas ref became null, aborting render')
          return
        }

        const context = canvas.getContext('2d')
        
        if (!context) {
          throw new Error('Failed to get 2D context from canvas')
        }

        canvas.width = viewport.width
        canvas.height = viewport.height
        console.log('[PdfCanvas] Canvas configured, starting render task')

        const renderTask = page.render({ 
          canvasContext: context, 
          viewport: viewport 
        } as any)
        
        // Store render task so we can cancel it if needed
        renderTaskRef.current = renderTask
        
        console.log('[PdfCanvas] Render task created, waiting...')
        await renderTask.promise
        
        // Check again if aborted before updating state
        if (abortController.signal.aborted) {
          console.log('[PdfCanvas] Effect was aborted after render, not updating state')
          return
        }

        console.log('[PdfCanvas] Render completed successfully!')
        renderTaskRef.current = null
        setLoading(false)
      } catch (err) {
        // Don't show error if it was cancelled
        if (err instanceof Error && err.message.includes('Rendering cancelled')) {
          console.log('[PdfCanvas] Render was cancelled')
          return
        }

        const message = err instanceof Error ? err.message : String(err)
        console.error('[PdfCanvas] Error during rendering:', message)
        console.error('[PdfCanvas] Error object:', err)
        
        // Only update state if not aborted
        if (!abortController.signal.aborted) {
          setError(message)
          setLoading(false)
        }
      }
    }

    renderPdf()

    // Cleanup: cancel render task and abort this effect's operations
    return () => {
      console.log('[PdfCanvas] Cleanup: aborting effect and cancelling render task')
      abortController.abort()
      if (renderTaskRef.current) {
        renderTaskRef.current.cancel()
        renderTaskRef.current = null
      }
    }
  }, [url, pageNum, onPagesLoaded])

  console.log('[PdfCanvas] Render state - loading:', loading, 'error:', error, 'has canvas:', !!canvasRef.current)

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 text-red-600">
        <AlertCircle className="h-6 w-6" />
        <p className="text-sm">{error}</p>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      {loading && (
        <div className="absolute flex flex-col items-center justify-center gap-2">
          <Loader className="h-6 w-6 animate-spin text-ink-soft" />
          <p className="text-sm text-ink-soft">Rendering page…</p>
        </div>
      )}
      <canvas ref={canvasRef} className="max-w-full" />
    </div>
  )
})
