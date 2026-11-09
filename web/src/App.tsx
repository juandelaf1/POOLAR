import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { clearToken, getToken } from './api/client'
import Home from './pages/Home'
import Login from './pages/Login'
import Approvals from './pages/Approvals'
import Modules from './pages/Modules'

export default function App() {
  const nav = useNavigate()
  const authed = !!getToken()
  return (
    <div className="app">
      <header className="topbar">
        <strong>POOLAR</strong>
        <nav>
          <NavLink to="/">Producto</NavLink>
          <NavLink to="/approvals">HITL/Aprobaciones</NavLink>
          <NavLink to="/modules">Módulos</NavLink>
          {authed ? <a href="#" onClick={(e)=>{e.preventDefault(); clearToken(); nav('/login')}}>Salir</a> : <NavLink to="/login">Ingresar</NavLink>}
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/modules" element={<Modules />} />
        </Routes>
      </main>
      <footer className="foot">Frontend fino: UI/UX. <strong>Autoridad (authz, tenant, HITL, ejecución) en API POOLAR.</strong></footer>
    </div>
  )
}
