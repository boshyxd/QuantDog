import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/layout'
import { HoneypotsPage } from '@/components/pages/honeypots'
import Visual from '@/components/pages/visual'
import { Toaster } from '@/components/ui/sonner'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/visual" element={<Visual />} />
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<HoneypotsPage />} />
            </Routes>
          </Layout>
        } />
      </Routes>
      <Toaster />
    </Router>
  )
}

export default App