import { Navigate, Route, Routes } from "react-router-dom"

import Footer from "./components/Footer"
import Navbar from "./components/Navbar"
import About from "./pages/About"
import Dashboard from "./pages/Dashboard"
import Generate from "./pages/Generate"
import Home from "./pages/Home"
import Validate from "./pages/Validate"

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-white to-slate-50 text-slate-900">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl px-4 py-8">{children}</main>
      <Footer />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Layout>
            <Generate />
          </Layout>
        }
      />
      <Route
        path="/validate"
        element={
          <Layout>
            <Validate />
          </Layout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
