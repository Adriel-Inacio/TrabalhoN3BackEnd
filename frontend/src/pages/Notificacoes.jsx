import { useEffect, useState } from 'react'
import { apiJson } from '../utils/api'
import Loading from '../components/Loading'
import styles from './Cultura.module.css'

export default function Notificacoes() {
  const [itens, setItens] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [versao, setVersao] = useState(0)
  useEffect(() => {
    let ativo = true
    setCarregando(true)
    apiJson('/api/notificacoes').then((dados) => { if (ativo) { setItens(dados); setErro('') } })
      .catch((e) => { if (ativo) setErro(e.message) })
      .finally(() => { if (ativo) setCarregando(false) })
    return () => { ativo = false }
  }, [versao])
  return <section className={styles.page}>
    <header className={styles.header}><div><h1>Notificações assíncronas</h1><p>Mensagens produzidas a partir da fila RabbitMQ e processadas pelo consumidor.</p></div><button className={styles.secondary} type="button" onClick={() => setVersao((v) => v + 1)}>Atualizar</button></header>
    {erro && <div className={styles.error} role="alert">{erro}</div>}
    {carregando ? <Loading mensagem="Consultando notificações..." /> : itens.length === 0 ? <div className={styles.empty}>Nenhuma notificação processada ainda. O recebimento é assíncrono.</div> : <div className={styles.cards}>{itens.map((i) => <div key={i.id} className={styles.card}><p>{i.mensagem}</p><span className={styles.info}>{new Date(i.criadoEm).toLocaleString('pt-BR')}</span></div>)}</div>}
  </section>
}
