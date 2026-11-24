import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import Home from './pages/Home'
import Login from './pages/Login'
import CadastroPublico from './pages/CadastroPublico'
import Worker from './pages/Worker'
import RegisterWorker from './pages/RegisterWorker'
import SelectWorker from './pages/SelectWorker'
import Eventos from './pages/Eventos'
import Ingressos from './pages/Ingressos'
import Clientes from './pages/Clientes'
import Notificacoes from './pages/Notificacoes'
import Sidebar from './components/Sidebar'
import Loading from './components/Loading'
import styles from './App.module.css'

function Exigir({ perfis, children }) {
  const { usuario } = useAuth()
  if (!usuario) return <Navigate to="/login" replace />
  return perfis.includes(usuario.perfil) ? children : <Navigate to="/" replace />
}

function Conteudo() {
  const { usuario, carregando } = useAuth()
  if (carregando) return <Loading mensagem="Verificando sessão..." />
  if (!usuario) return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/cadastro" element={<CadastroPublico />} />
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes>
  return <div className={styles.appLayout}>
    <Sidebar />
    <main className={styles.appContent}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/eventos" element={<Eventos />} />
        <Route path="/ingressos" element={<Ingressos />} />
        <Route path="/notificacoes" element={<Notificacoes />} />
        <Route path="/clientes" element={<Exigir perfis={['ADMIN', 'FUNCIONARIO']}><Clientes /></Exigir>} />
        <Route path="/funcionarios" element={<Exigir perfis={['ADMIN']}><Worker /></Exigir>}>
          <Route index element={<SelectWorker />} />
          <Route path="novo" element={<RegisterWorker />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  </div>
}

export default function App() {
  return <AuthProvider><Conteudo /></AuthProvider>
}
