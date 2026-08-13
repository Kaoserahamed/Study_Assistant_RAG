import type { Citation, StudyDocument } from '@/types'
import { inferKindFromFileName } from '@/utils/format'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT ? parseInt(import.meta.env.VITE_API_TIMEOUT) : 30000

// Supported file types
const SUPPORTED_FORMATS = ['pdf', 'docx', 'pptx', 'ppt', 'txt']

/**
 * Validate if file format is supported
 */
export function isFileSupported(file: File): boolean {
  const ext = file.name.split('.').pop()?.toLowerCase()
  return ext ? SUPPORTED_FORMATS.includes(ext) : false
}

export function getSupportedFormats(): string {
  return SUPPORTED_FORMATS.map(f => f.toUpperCase()).join(', ')
}

/**
 * Make authenticated API request
 */
async function apiCall(
  endpoint: string,
  options: RequestInit = {},
  includeAuth: boolean = true,
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = new Headers(options.headers)

  if (includeAuth) {
    const token = localStorage.getItem('access_token')
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    // Token expired, redirect to login
    localStorage.removeItem('access_token')
    window.location.href = '/auth/login'
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response
}

/**
 * Fetch all documents for current user
 */
export async function fetchDocuments(): Promise<StudyDocument[]> {
  try {
    const response = await apiCall('/documents/')
    const documents = await response.json()

    console.log('[API] fetchDocuments raw response:', documents)
    console.log('[API] fetchDocuments count:', documents.length)

    const mapped = documents.map((doc: any) => {
      const result = {
        id: `doc-${doc.id}`,
        title: doc.filename,
        kind: inferKindFromFileName(doc.filename),
        courseTag: 'Uploaded',
        status: 'ready',
        pageCount: doc.page_count,
        sizeLabel: 'N/A',
        uploadedAt: doc.created_at,
        thumbnailColor: 'bg-denim',
        excerpt: `${doc.page_count} pages - Ready for search`,
      }
      console.log(`[API] Mapped doc ${doc.id}:`, result)
      return result
    })

    console.log('[API] fetchDocuments mapped result:', mapped)
    return mapped
  } catch (error) {
    console.error('Failed to fetch documents:', error)
    throw error
  }
}

/**
 * Upload a document file
 */
export async function uploadDocument(file: File, courseTag?: string): Promise<StudyDocument> {
  if (!isFileSupported(file)) {
    throw new Error(`Unsupported file format. Supported formats: ${getSupportedFormats()}`)
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiCall('/documents/upload', {
      method: 'POST',
      body: formData,
    })

    const doc = await response.json()

    return {
      id: `doc-${doc.id}`,
      title: doc.filename,
      kind: inferKindFromFileName(doc.filename),
      courseTag: courseTag || 'Uploaded',
      status: 'ready',
      pageCount: doc.page_count,
      sizeLabel: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      uploadedAt: doc.created_at,
      thumbnailColor: 'bg-denim',
      excerpt: `${doc.page_count} pages - Ready for semantic search`,
    }
  } catch (error) {
    console.error('Failed to upload document:', error)
    throw error
  }
}

/**
 * Register a new user
 */
export async function registerUser(
  email: string,
  name: string,
  password: string,
): Promise<{ id: number; email: string; name: string }> {
  try {
    const response = await apiCall(
      '/auth/register',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, password }),
      },
      false,
    )

    return await response.json()
  } catch (error) {
    console.error('Registration failed:', error)
    throw error
  }
}

/**
 * Login user
 */
export async function loginUser(email: string, password: string): Promise<string> {
  try {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await apiCall(
      '/auth/login',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      },
      false,
    )

    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    return data.access_token
  } catch (error) {
    console.error('Login failed:', error)
    throw error
  }
}

/**
 * Get current user
 */
export async function getCurrentUser(): Promise<{ id: number; email: string; name: string }> {
  try {
    const response = await apiCall('/auth/me')
    return await response.json()
  } catch (error) {
    console.error('Failed to get current user:', error)
    throw error
  }
}

/**
 * Search documents
 */
export async function searchDocuments(
  query: string,
  topK: number = 5,
): Promise<Citation[]> {
  try {
    const response = await apiCall('/search/documents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK }),
    })

    const data = await response.json()

    return data.results.map((result: any) => {
      const documentTitle = result.documentTitle || `Document ${result.document_id}`
      return {
        id: result.chunk_id || result.id,
        documentId: `doc-${result.document_id}`,
        documentTitle,
        documentKind: result.documentKind || inferKindFromFileName(documentTitle),
        page: result.page_number || result.page,
        snippet: result.content || result.snippet,
      }
    })
  } catch (error) {
    console.error('Search failed:', error)
    throw error
  }
}

/**
 * Chat operations
 */
export async function createConversation(title?: string): Promise<any> {
  try {
    const response = await apiCall('/chat/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    })
    return await response.json()
  } catch (error) {
    console.error('Failed to create conversation:', error)
    throw error
  }
}

export async function listConversations(): Promise<any[]> {
  try {
    const response = await apiCall('/chat/conversations')
    return await response.json()
  } catch (error) {
    console.error('Failed to list conversations:', error)
    throw error
  }
}

export async function getConversation(conversationId: number): Promise<any> {
  try {
    const response = await apiCall(`/chat/conversations/${conversationId}`)
    return await response.json()
  } catch (error) {
    console.error('Failed to get conversation:', error)
    throw error
  }
}

export async function deleteConversation(conversationId: number): Promise<void> {
  try {
    await apiCall(`/chat/conversations/${conversationId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('Failed to delete conversation:', error)
    throw error
  }
}

export async function sendMessage(
  conversationId: number,
  query: string,
  documentIds?: string[],
): Promise<any> {
  try {
    const response = await apiCall(
      `/chat/conversations/${conversationId}/messages`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, document_ids: documentIds }),
      },
    )
    return await response.json()
  } catch (error) {
    console.error('Failed to send message:', error)
    throw error
  }
}


/**
 * Delete a document
 */
export async function deleteDocument(documentId: string): Promise<void> {
  try {
    const id = documentId.replace('doc-', '')
    await apiCall(`/documents/${id}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('Failed to delete document:', error)
    throw error
  }
}

/**
 * Get document PDF file URL for embedding in iframe or Document viewer
 */
export function getDocumentFileUrl(documentId: string): string {
  const id = documentId.replace('doc-', '')
  return `${API_BASE_URL}/documents/${id}/file`
}
