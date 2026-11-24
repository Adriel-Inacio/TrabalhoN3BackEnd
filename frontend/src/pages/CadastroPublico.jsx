import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { apiJson, requisicaoJson } from '../utils/api'
import { formatarTelefone, somenteNumeros } from '../utils/mascaras'
import styles from './Auth.module.css'

export default function CadastroPublico() {
  const { usuario } = useAuth()
  const [dados, setDados] = useState({ nome: '', email: '', telefone: '', senha: '', confirmar: '' })
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const atualizar = (campo, valor) => setDados((atual) => ({ ...atual, [campo]: valor }))
  if (usuario) return <Navigate to="/" replace />

  const salvar = async (evento) => {
    evento.preventDefault()
    if (salvando) return
    if (dados.senha !== dados.confirmar) {
      setErro('As senhas não coincidem.')
      return
    }
    setErro('')
    setSalvando(true)
    try {
      await apiJson('/api/auth/cadastro', requisicaoJson('POST', {
        nome: dados.nome, email: dados.email, telefone: somenteNumeros(dados.telefone), senha: dados.senha
      }))
      setSucesso(true)
    } catch (falha) {
      setErro(falha.message)
    } finally {
      setSalvando(false)
    }
  }

  return <div className={styles.center}>
    <section className={styles.card}>
      <h1>Cadastro de cliente</h1>
      <p>Crie sua conta para consultar eventos e adquirir ingressos.</p>
      {erro && <div role="alert" className={styles.error}>{erro}</div>}
      {sucesso ? <div role="status" className={styles.success}>Conta criada com sucesso. <Link to="/login">Ir para o login</Link></div> :
        <form className={styles.form} onSubmit={salvar}>
          <div className={styles.field}><label htmlFor="novo-nome">Nome completo</label><input id="novo-nome" required maxLength={80} value={dados.nome} onChange={(e) => atualizar('nome', e.target.value)} /></div>
          <div className={styles.field}><label htmlFor="novo-email">E-mail</label><input id="novo-email" type="email" required maxLength={80} autoComplete="email" value={dados.email} onChange={(e) => atualizar('email', e.target.value)} /></div>
          <div className={styles.field}><label htmlFor="novo-tel">Telefone</label><input id="novo-tel" type="tel" required value={dados.telefone} onChange={(e) => atualizar('telefone', formatarTelefone(e.target.value))} /></div>
          <div className={styles.field}><label htmlFor="novo-senha">Senha</label><input id="novo-senha" type="password" required minLength={10} maxLength={128} autoComplete="new-password" value={dados.senha} onChange={(e) => atualizar('senha', e.target.value)} /></div>
          <div className={styles.field}><label htmlFor="novo-confirmar">Confirmar senha</label><input id="novo-confirmar" type="password" required minLength={10} autoComplete="new-password" value={dados.confirmar} onChange={(e) => atualizar('confirmar', e.target.value)} /></div>
          <button className={styles.action} type="submit" disabled={salvando}>{salvando ? 'Cadastrando...' : 'Criar conta'}</button>
        </form>
      }
      <div className={styles.links}><Link to="/login">Voltar ao login</Link></div>
    </section>
  </div>
}
