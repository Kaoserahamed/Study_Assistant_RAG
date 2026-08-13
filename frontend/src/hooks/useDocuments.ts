import { useCallback, useEffect, useState } from 'react'
import type { StudyDocument, UploadTask } from '@/types'
import { fetchDocuments, uploadDocument, isFileSupported, getSupportedFormats } from '@/services/api'
import { bytesToLabel } from '@/utils/format'

export function useDocuments() {
  const [documents, setDocuments] = useState<StudyDocument[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        console.log('[useDocuments] Fetching documents...')
        setIsLoading(true)
        setError(null)
        
        const docs = await fetchDocuments()
        console.log('[useDocuments] Fetched', docs.length, 'documents')
        setDocuments(docs)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load documents'
        console.error('[useDocuments] Error:', message)
        setError(message)
        setDocuments([])
      } finally {
        setIsLoading(false)
      }
    }

    loadDocuments()
    
    // Refresh documents every 10 seconds to pick up new uploads
    const interval = setInterval(loadDocuments, 10000)
    
    return () => clearInterval(interval)
  }, [])

  const addFiles = useCallback((files: File[], courseTag = 'Unsorted') => {
    // Validate files
    const unsupportedFiles = files.filter((f) => !isFileSupported(f))
    if (unsupportedFiles.length > 0) {
      setError(
        `Unsupported file format. Supported formats: ${getSupportedFormats()}`,
      )
      return
    }

    files.forEach((file) => {
      const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
      const task: UploadTask = {
        id: taskId,
        fileName: file.name,
        sizeLabel: bytesToLabel(file.size),
        progress: 0,
        status: 'queued',
      }
      setUploadTasks((prev) => [task, ...prev])

      // Simulate a progressive upload
      const interval = setInterval(() => {
        setUploadTasks((prev) =>
          prev.map((t) => (t.id === taskId ? { ...t, progress: Math.min(t.progress + 22, 90) } : t)),
        )
      }, 220)

      setTimeout(async () => {
        try {
          clearInterval(interval)
          setUploadTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, progress: 100, status: 'processing' } : t)))
          
          const newDoc = await uploadDocument(file, courseTag)
          setDocuments((prev) => [newDoc, ...prev])
          
          // Remove task after success
          setTimeout(() => {
            setUploadTasks((prev) => prev.filter((t) => t.id !== taskId))
          }, 1000)
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Upload failed'
          setUploadTasks((prev) =>
            prev.map((t) =>
              t.id === taskId ? { ...t, status: 'failed', progress: 0 } : t,
            ),
          )
          setError(errorMessage)
        }
      }, 1100)
    })
  }, [])

  const removeDocument = useCallback((docId: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== docId))
  }, [])

  return { documents, isLoading, uploadTasks, addFiles, error, setError, removeDocument }
}

