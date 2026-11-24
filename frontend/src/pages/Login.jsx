import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './Auth.module.css'

export default function Login() {
  const { usuario, login } = useAuth()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (usuario) return <Navigate to="/" replace />

  const entrar = async (evento) => {
    evento.preventDefault()
    if (enviando) return
    setEnviando(true)
    setErro('')
    try {
      await login(email, senha)
    } catch (falha) {
      setErro(falha.message)
    } finally {
      setEnviando(false)
    }
  }

  return <div className={styles.center}>
    <section className={styles.card}>
      <h1>CulturaPass</h1>
      <p>Acesse sua conta para continuar.</p>
      {erro && <div role="alert" className={styles.error}>{erro}</div>}
      <form className={styles.form} onSubmit={entrar}>
        <div className={styles.field}><label htmlFor="login-email">E-mail</label><input id="login-email" type="email" autoComplete="username" required maxLength={80} value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="login-senha">Senha</label><input id="login-senha" type="password" autoComplete="current-password" required value={senha} onChange={(e) => setSenha(e.target.value)} /></div>
        <button className={styles.action} type="submit" disabled={enviando}>{enviando ? 'Entrando...' : 'Entrar'}</button>
      </form>
      <div className={styles.links}><Link to="/cadastro">Criar conta de cliente</Link></div>
    </section>
  </div>
}
