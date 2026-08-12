import { useCallback, useEffect, useState } from 'react'
import type { StudyDocument, UploadTask } from '@/types'
import { fetchDocuments, uploadDocument } from '@/services/api'
import { bytesToLabel } from '@/utils/format'

export function useDocuments() {
  const [documents, setDocuments] = useState<StudyDocument[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([])

  useEffect(() => {
    fetchDocuments().then((docs) => {
      setDocuments(docs)
      setIsLoading(false)
    })
  }, [])

  const addFiles = useCallback((files: File[], courseTag = 'Unsorted') => {
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

      // Simulate a progressive upload, then hand off to the "backend" for processing.
      const interval = setInterval(() => {
        setUploadTasks((prev) =>
          prev.map((t) => (t.id === taskId ? { ...t, progress: Math.min(t.progress + 22, 100) } : t)),
        )
      }, 220)

      setTimeout(async () => {
        clearInterval(interval)
        setUploadTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, progress: 100 } : t)))
        const newDoc = await uploadDocument(file, courseTag)
        setDocuments((prev) => [newDoc, ...prev])

        // Simulate the backend finishing indexing a few seconds later.
        setTimeout(() => {
          setDocuments((prev) =>
            prev.map((d) => (d.id === newDoc.id ? { ...d, status: 'ready', progress: undefined } : d)),
          )
        }, 3200)
      }, 1100)
    })
  }, [])

  return { documents, isLoading, uploadTasks, addFiles }
}
