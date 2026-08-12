import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { OverviewPage } from '@/pages/OverviewPage'
import { UploadPage } from '@/pages/UploadPage'
import { LibraryPage } from '@/pages/LibraryPage'
import { DocumentViewerPage } from '@/pages/DocumentViewerPage'
import { ChatPage } from '@/pages/ChatPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/library/:docId" element={<DocumentViewerPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
