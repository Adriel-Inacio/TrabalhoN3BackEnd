import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import styles from './Portal.module.css'

export default function Home() {
  const { usuario } = useAuth()
  const titulo = usuario.perfil === 'ADMIN' ? 'Painel administrativo' : usuario.perfil === 'FUNCIONARIO' ? 'Painel do organizador' : 'Meu CulturaPass'
  const paginas = [
    { to: '/eventos', titulo: 'Eventos culturais', detalhe: 'Programação e vagas disponíveis' },
    { to: '/ingressos', titulo: usuario.perfil === 'CLIENTE' ? 'Meus ingressos' : 'Gerenciar ingressos', detalhe: 'Aquisições, regras e histórico' },
    { to: '/notificacoes', titulo: 'Notificações', detalhe: 'Mensagens processadas pelo RabbitMQ' },
    ...(usuario.perfil !== 'CLIENTE' ? [{ to: '/clientes', titulo: 'Clientes', detalhe: 'Cadastro e consulta dos compradores' }] : []),
    ...(usuario.perfil === 'ADMIN' ? [{ to: '/funcionarios', titulo: 'Funcionários', detalhe: 'Contas e credenciais dos organizadores' }] : [])
  ]
  return <section className={styles.page}>
    <h1>{titulo}</h1><p>Bem-vindo ao CulturaPass, {usuario.nome}. Gerencie eventos e ingressos culturais de maneira integrada.</p>
    <div className={styles.cards}>{paginas.map((pagina) => <Link key={pagina.to} to={pagina.to} className={styles.card}><strong>{pagina.titulo}</strong><span>{pagina.detalhe}</span></Link>)}</div>
  </section>
}
