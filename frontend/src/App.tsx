import './App.css'
import { Layout } from '@/components/layout/layout'
import { HoneypotsPage } from '@/components/pages/honeypots'
import { Toaster } from '@/components/ui/sonner'

function App() {
  return (
    <Layout>
      <HoneypotsPage />
      <Toaster />
    </Layout>
  )
}

export default App