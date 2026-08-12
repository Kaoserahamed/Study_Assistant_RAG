import type { ChatThread, StudyDocument } from '@/types'

export const documents: StudyDocument[] = [
  {
    id: 'doc-1',
    title: 'Introduction to Machine Learning, 3rd Ed.',
    kind: 'textbook',
    courseTag: 'CS 4780',
    status: 'ready',
    pageCount: 412,
    sizeLabel: '18.2 MB',
    uploadedAt: '2026-08-03',
    thumbnailColor: 'bg-denim',
    excerpt:
      'Chapter 4 introduces the distinction between supervised and unsupervised learning, covering loss functions, labeled training sets, and clustering objectives.',
  },
  {
    id: 'doc-2',
    title: 'Week 6 — Unsupervised Learning',
    kind: 'lecture-notes',
    courseTag: 'CS 4780',
    status: 'ready',
    pageCount: 14,
    sizeLabel: '2.1 MB',
    uploadedAt: '2026-08-05',
    thumbnailColor: 'bg-mint',
    excerpt:
      'Handwritten notes covering k-means, hierarchical clustering, and comparison points against supervised baselines from lecture discussion.',
  },
  {
    id: 'doc-3',
    title: 'Lecture 12 Slides — Learning Paradigms',
    kind: 'slides',
    courseTag: 'CS 4780',
    status: 'ready',
    pageCount: 38,
    sizeLabel: '6.4 MB',
    uploadedAt: '2026-08-05',
    thumbnailColor: 'bg-highlighter-dark',
    excerpt:
      'Slide deck contrasting supervised, unsupervised, and semi-supervised learning with worked examples and a summary table on slide 9.',
  },
  {
    id: 'doc-4',
    title: 'Problem Set 3 Handout',
    kind: 'handout',
    courseTag: 'CS 4780',
    status: 'processing',
    pageCount: 6,
    sizeLabel: '820 KB',
    uploadedAt: '2026-08-10',
    progress: 64,
    thumbnailColor: 'bg-rust',
    excerpt: 'Practice problems on classification versus clustering, due next Friday.',
  },
  {
    id: 'doc-5',
    title: 'Linear Algebra Review Packet',
    kind: 'handout',
    courseTag: 'MATH 2210',
    status: 'ready',
    pageCount: 22,
    sizeLabel: '3.9 MB',
    uploadedAt: '2026-07-28',
    thumbnailColor: 'bg-rust',
    excerpt: 'Refresher on eigenvectors, matrix decompositions, and norms used throughout the ML course.',
  },
  {
    id: 'doc-6',
    title: 'Week 7 — Neural Network Foundations',
    kind: 'lecture-notes',
    courseTag: 'CS 4780',
    status: 'queued',
    pageCount: 11,
    sizeLabel: '1.6 MB',
    uploadedAt: '2026-08-11',
    thumbnailColor: 'bg-mint',
    excerpt: 'Notes queued for processing — will be searchable shortly.',
  },
]

export const chatThreads: ChatThread[] = [
  {
    id: 'thread-1',
    title: 'Supervised vs. unsupervised learning',
    createdAt: '2026-08-11T09:14:00Z',
    documentIds: ['doc-1', 'doc-2', 'doc-3'],
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: 'Explain the difference between supervised and unsupervised learning.',
        createdAt: '2026-08-11T09:14:00Z',
      },
      {
        id: 'm2',
        role: 'assistant',
        content:
          "Supervised learning trains a model on labeled examples, pairs of inputs and known correct outputs, so the model learns to map new inputs to outputs by minimizing error against those labels [1]. Your lecture notes frame this as \"learning with an answer key\": the algorithm gets graded during training. Unsupervised learning, by contrast, works with unlabeled data and looks for structure on its own, such as grouping similar points together in clustering or reducing dimensionality [2]. The slide deck's summary table puts it plainly: supervised tasks predict a target variable, while unsupervised tasks describe the shape of the data itself [3].\n\nA useful way to hold both in mind: supervised learning answers \"what is this?\" using examples you've already labeled, while unsupervised learning answers \"what patterns exist here?\" without being told the answer in advance.",
        createdAt: '2026-08-11T09:14:04Z',
        citations: [
          {
            id: 'c1',
            documentId: 'doc-1',
            documentTitle: 'Introduction to Machine Learning, 3rd Ed.',
            documentKind: 'textbook',
            page: 118,
            snippet:
              'In supervised learning, the learner receives a training set of input-output pairs and must infer a function that generalizes to unseen inputs.',
          },
          {
            id: 'c2',
            documentId: 'doc-2',
            documentTitle: 'Week 6 — Unsupervised Learning',
            documentKind: 'lecture-notes',
            page: 3,
            snippet:
              'Unsupervised = no answer key. The model looks for structure: clusters, densities, or lower-dimensional shape.',
          },
          {
            id: 'c3',
            documentId: 'doc-3',
            documentTitle: 'Lecture 12 Slides — Learning Paradigms',
            documentKind: 'slides',
            page: 9,
            snippet:
              'Summary — Supervised: predicts a labeled target. Unsupervised: describes structure with no target.',
          },
        ],
      },
    ],
  },
]
