export type DocumentKind = 'textbook' | 'lecture-notes' | 'slides' | 'handout'

export type DocumentStatus = 'queued' | 'processing' | 'ready' | 'failed'

export interface StudyDocument {
  id: string
  title: string
  kind: DocumentKind
  courseTag: string
  status: DocumentStatus
  pageCount: number
  sizeLabel: string
  uploadedAt: string
  progress?: number
  thumbnailColor: string
  excerpt: string
}

export interface Citation {
  id: string
  documentId: string
  documentTitle: string
  documentKind: DocumentKind
  page: number
  snippet: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  createdAt: string
  isStreaming?: boolean
}

export interface ChatThread {
  id: string
  title: string
  createdAt: string
  documentIds: string[]
  messages: ChatMessage[]
}

export interface UploadTask {
  id: string
  fileName: string
  sizeLabel: string
  progress: number
  status: DocumentStatus
}
