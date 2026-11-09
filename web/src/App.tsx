import { NavLink, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import Approvals from './pages/Approvals'
import Modules from './pages/Modules'

export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <strong>POOLAR</strong>
        <nav>
          <NavLink to="/">Producto</NavLink>
          <NavLink to="/approvals">HITL/Aprobaciones</NavLink>
          <NavLink to="/modules">Módulos</NavLink>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/modules" element={<Modules />} />
        </Routes>
      </main>
      <footer className="foot">Frontend fino: UI/UX. <strong>Autoridad (authz, tenant, HITL, ejecución) en API POOLAR.</strong></footer>
    </div>
  )
}
