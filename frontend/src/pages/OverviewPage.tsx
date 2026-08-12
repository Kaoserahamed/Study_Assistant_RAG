import { BookMarked, MessagesSquare, Sparkles, UploadCloud } from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatCard } from '@/components/dashboard/StatCard'
import { DocumentCard } from '@/components/documents/DocumentCard'
import { SuggestedQuestionCard } from '@/components/dashboard/SuggestedQuestionCard'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useDocuments } from '@/hooks/useDocuments'

const suggestedQuestions = [
  'Explain the difference between supervised and unsupervised learning.',
  'Summarize the key trade-offs between bias and variance.',
  'What did lecture 12 say about semi-supervised learning?',
  'Compare k-means clustering to hierarchical clustering.',
]

export function OverviewPage() {
  const { documents, isLoading } = useDocuments()
  const readyCount = documents.filter((d) => d.status === 'ready').length
  const processingCount = documents.filter((d) => d.status !== 'ready').length
  const recentDocs = documents.slice(0, 3)

  return (
    <div className="max-w-6xl mx-auto px-6 md:px-10 py-8 md:py-10">
      <PageHeader
        eyebrow="Welcome back"
        title="What are you studying today?"
        description="Upload course materials once, then ask questions in plain language — every answer traces back to the exact page it came from."
        action={
          <Link to="/chat">
            <Button size="md">
              <MessagesSquare className="h-4 w-4" />
              Ask a question
            </Button>
          </Link>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard icon={BookMarked} label="Ready to query" value={String(readyCount)} tone="bg-mint-dark" />
        <StatCard icon={UploadCloud} label="Processing" value={String(processingCount)} tone="bg-highlighter-dark" />
        <StatCard icon={Sparkles} label="Questions asked" value="27" tone="bg-denim" />
        <StatCard icon={BookMarked} label="Courses" value="2" tone="bg-rust" />
      </div>

      <div className="grid lg:grid-cols-5 gap-8">
        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-lg text-ink">Recently uploaded</h2>
            <Link to="/library" className="text-xs font-medium text-denim hover:underline">
              View library
            </Link>
          </div>
          {isLoading ? (
            <div className="grid sm:grid-cols-2 gap-4">
              {[0, 1].map((i) => (
                <div key={i} className="h-44 rounded-card bg-white border border-paper-line animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {recentDocs.map((doc) => (
                <DocumentCard key={doc.id} doc={doc} />
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <h2 className="font-display text-lg text-ink mb-4">Try asking</h2>
          <div className="space-y-2.5">
            {suggestedQuestions.map((q) => (
              <SuggestedQuestionCard key={q} question={q} />
            ))}
          </div>

          <Card className="mt-5 bg-ink text-paper border-none">
            <p className="text-xs font-mono uppercase tracking-widest text-highlighter mb-2">How it works</p>
            <p className="text-sm leading-relaxed text-paper/85">
              Every answer is generated primarily from the materials you've uploaded. Claims are paired with
              highlighter-tab citations you can click to jump straight to the source page.
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}
