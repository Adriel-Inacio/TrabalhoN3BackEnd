import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './Sidebar.module.css'

export default function Sidebar() {
  const [menuAberto, setMenuAberto] = useState(false)
  const { usuario, logout } = useAuth()
  const paginas = [
    { to: '/', label: 'Início', perfis: ['ADMIN', 'FUNCIONARIO', 'CLIENTE'] },
    { to: '/eventos', label: 'Eventos', perfis: ['ADMIN', 'FUNCIONARIO', 'CLIENTE'] },
    { to: '/ingressos', label: 'Ingressos', perfis: ['ADMIN', 'FUNCIONARIO', 'CLIENTE'] },
    { to: '/notificacoes', label: 'Notificações', perfis: ['ADMIN', 'FUNCIONARIO', 'CLIENTE'] },
    { to: '/clientes', label: 'Clientes', perfis: ['ADMIN', 'FUNCIONARIO'] },
    { to: '/funcionarios', label: 'Funcionários', perfis: ['ADMIN'] }
  ]
  return <aside className={styles.sidebar}>
    <nav className={styles.nav} aria-label="Menu principal">
      <div className={styles.mobileHeader}>
        <h1 className={styles.title}>CulturaPass</h1>
        <button type="button" className={styles.menuButton} onClick={() => setMenuAberto(!menuAberto)} aria-expanded={menuAberto}>{menuAberto ? '✕' : '☰'}</button>
      </div>
      <div className={styles.identity}><strong>{usuario.nome}</strong><span>{usuario.perfil === 'ADMIN' ? 'Administrador' : usuario.perfil === 'FUNCIONARIO' ? 'Funcionário' : 'Cliente'}</span></div>
      {paginas.filter((p) => p.perfis.includes(usuario.perfil)).map(({ to, label }) =>
        <NavLink key={to} to={to} end={to === '/'} onClick={() => setMenuAberto(false)} className={({ isActive }) => [styles.link, isActive ? styles.active : '', menuAberto ? styles.menuOpen : ''].filter(Boolean).join(' ')}><span className={styles.linkText}>{label}</span></NavLink>
      )}
      <button type="button" className={`${styles.link} ${styles.logout} ${menuAberto ? styles.menuOpen : ''}`} onClick={() => logout().catch(() => {})}>Sair da conta</button>
    </nav>
  </aside>
}
