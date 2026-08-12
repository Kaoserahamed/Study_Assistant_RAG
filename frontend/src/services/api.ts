import { chatThreads, documents } from '@/data/mockData'
import type { Citation, StudyDocument } from '@/types'
import { inferKindFromFileName } from '@/utils/format'

// This module simulates a backend for the RAG study-assistant product.
// Swap the bodies of these functions for real `fetch` calls to your API
// (e.g. POST /documents, POST /chat) — the component layer only depends
// on these function signatures, not on how the data is produced.

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

let documentStore: StudyDocument[] = [...documents]

export async function fetchDocuments(): Promise<StudyDocument[]> {
  await delay(300)
  return documentStore
}

export async function uploadDocument(file: File, courseTag: string): Promise<StudyDocument> {
  const newDoc: StudyDocument = {
    id: `doc-${Date.now()}`,
    title: file.name.replace(/\.(pdf|pptx|docx|txt)$/i, ''),
    kind: inferKindFromFileName(file.name),
    courseTag: courseTag || 'Unsorted',
    status: 'queued',
    pageCount: Math.floor(Math.random() * 30) + 4,
    sizeLabel: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
    uploadedAt: new Date().toISOString(),
    thumbnailColor: 'bg-denim',
    excerpt: 'Waiting to be indexed. This will be searchable once processing finishes.',
  }
  documentStore = [newDoc, ...documentStore]
  return newDoc
}

export async function fetchChatThreads() {
  await delay(200)
  return chatThreads
}

const SAMPLE_CITATIONS: Citation[] = [
  {
    id: 'gen-c1',
    documentId: 'doc-1',
    documentTitle: 'Introduction to Machine Learning, 3rd Ed.',
    documentKind: 'textbook',
    page: 121,
    snippet:
      'A key trade-off in model selection is the balance between bias and variance as capacity increases.',
  },
  {
    id: 'gen-c2',
    documentId: 'doc-3',
    documentTitle: 'Lecture 12 Slides — Learning Paradigms',
    documentKind: 'slides',
    page: 14,
    snippet: 'Worked example: cross-validation curve showing underfitting versus overfitting regions.',
  },
]

export async function askQuestion(
  question: string,
  _documentIds: string[],
): Promise<{ content: string; citations: Citation[] }> {
  await delay(1400)
  return {
    content: `Based on the materials you've uploaded, here's a grounded answer to "${question}":\n\nThe source materials frame this around the balance between how closely a model fits its training data and how well it generalizes to new examples. The textbook chapter walks through the formal trade-off, while the slide deck's worked example shows what under- and over-fitting look like on a validation curve.\n\nIn short: a model that's too simple misses real patterns (underfitting), while one that's too flexible memorizes noise instead of signal (overfitting) — the sweet spot is found by validating against held-out data.`,
    citations: SAMPLE_CITATIONS,
  }
}
