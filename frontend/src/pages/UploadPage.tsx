import { useState } from 'react'
import { PageHeader } from '@/components/layout/PageHeader'
import { UploadDropzone } from '@/components/documents/UploadDropzone'
import { UploadTaskRow } from '@/components/documents/UploadTaskRow'
import { Card } from '@/components/ui/Card'
import { TextField } from '@/components/ui/TextField'
import { useDocuments } from '@/hooks/useDocuments'
import { DocumentGrid } from '@/components/documents/DocumentGrid'

export function UploadPage() {
  const { documents, uploadTasks, addFiles } = useDocuments()
  const [courseTag, setCourseTag] = useState('CS 4780')

  const recentlyAdded = documents.filter((d) => d.status !== 'ready').slice(0, 6)

  return (
    <div className="max-w-5xl mx-auto px-6 md:px-10 py-8 md:py-10">
      <PageHeader
        eyebrow="Build your library"
        title="Upload study materials"
        description="Add PDF textbooks, lecture notes, slide decks, or handouts. We'll extract and index the text so it becomes searchable and citable."
      />

      <div className="grid md:grid-cols-[1fr_220px] gap-4 mb-6">
        <UploadDropzone onFiles={(files) => addFiles(files, courseTag)} />
        <Card className="flex flex-col justify-center">
          <TextField
            id="course-tag"
            label="Course tag"
            placeholder="e.g. CS 4780"
            value={courseTag}
            onChange={(e) => setCourseTag(e.target.value)}
          />
          <p className="text-[11px] text-ink-faint mt-2 leading-relaxed">
            Applied to files you upload next, so materials from the same class stay grouped in your library.
          </p>
        </Card>
      </div>

      {uploadTasks.length > 0 && (
        <Card className="mb-8" padded={false}>
          <div className="px-5 pt-4 pb-1">
            <p className="text-sm font-medium text-ink">Uploading</p>
          </div>
          <div className="px-5 pb-2">
            {uploadTasks.map((task) => (
              <UploadTaskRow key={task.id} task={task} />
            ))}
          </div>
        </Card>
      )}

      {recentlyAdded.length > 0 && (
        <div>
          <h2 className="font-display text-lg text-ink mb-4">Indexing now</h2>
          <DocumentGrid docs={recentlyAdded} />
        </div>
      )}
    </div>
  )
}
