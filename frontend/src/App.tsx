import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Home from './pages/Home'
import Results from './pages/Results'
import ErrorBoundary from './components/ErrorBoundary'
import { CareerGuidanceProvider } from './context/CareerGuidanceContext'

function App() {
  return (
    <ErrorBoundary>
      <CareerGuidanceProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-secondary-50 to-primary-50">
            <Header />
            <main id="main-content" className="container-responsive py-8">
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/results" element={<Results />} />
                </Routes>
              </ErrorBoundary>
            </main>
          </div>
        </Router>
      </CareerGuidanceProvider>
    </ErrorBoundary>
  )
}

export default App
