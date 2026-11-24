import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { apiJson, requisicaoJson } from '../utils/api'
import Paginacao from '../components/Paginacao'
import Loading from '../components/Loading'
import Alert from '../components/Alert'
import styles from './Cultura.module.css'

export default function Ingressos() {
  const { usuario } = useAuth()
  const cliente = usuario.perfil === 'CLIENTE'
  const admin = usuario.perfil === 'ADMIN'
  const [eventos, setEventos] = useState([])
  const [clientes, setClientes] = useState([])
  const [pagina, setPagina] = useState(1)
  const [paginas, setPaginas] = useState(1)
  const [total, setTotal] = useState(0)
  const [ingressos, setIngressos] = useState([])
  const [pesquisa, setPesquisa] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('')
  const [versao, setVersao] = useState(0)
  const [eventoId, setEventoId] = useState('')
  const [clienteId, setClienteId] = useState('')
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [processando, setProcessando] = useState(false)

  useEffect(() => {
    let ativo = true
    const clientesReq = cliente ? Promise.resolve(null) : apiJson('/api/clientes?page=1&perPage=100&sort=nome')
    Promise.all([apiJson('/api/eventos?page=1&perPage=100&sort=dataHora'), clientesReq])
      .then(([dadosEventos, dadosClientes]) => {
        if (!ativo) return
        setEventos(dadosEventos.items)
        setClientes(dadosClientes?.items || [])
      }).catch((e) => { if (ativo) setErro(e.message) })
    return () => { ativo = false }
  }, [cliente, versao])

  useEffect(() => {
    let ativo = true
    setCarregando(true)
    const params = new URLSearchParams({ page: pagina, perPage: 10, sort: 'adquiridoEm', ordem: 'desc', q: pesquisa })
    if (filtroStatus) params.set('status', filtroStatus)
    apiJson(`/api/ingressos?${params}`).then((dados) => {
      if (!ativo) return
      setIngressos(dados.items)
      setPaginas(dados.pages)
      setTotal(dados.total)
    }).catch((e) => { if (ativo) setErro(e.message) })
      .finally(() => { if (ativo) setCarregando(false) })
    return () => { ativo = false }
  }, [pagina, pesquisa, filtroStatus, versao])

  const comprar = async (e) => {
    e.preventDefault()
    if (processando) return
    setProcessando(true)
    setErro('')
    setMensagem('')
    try {
      const corpo = { eventoId: Number(eventoId) }
      if (!cliente) corpo.clienteId = Number(clienteId)
      await apiJson('/api/ingressos', requisicaoJson('POST', corpo))
      setMensagem('Ingresso adquirido com sucesso. A notificação será processada de forma assíncrona.')
      setPagina(1)
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }

  const atualizar = async (ingresso, status) => {
    if (!window.confirm(`${status === 'CANCELADO' ? 'Cancelar' : 'Reativar'} o ingresso #${ingresso.id}?`)) return
    setProcessando(true)
    setErro('')
    setMensagem('')
    try {
      await apiJson(`/api/ingressos/${ingresso.id}`, requisicaoJson('PUT', { status }))
      setMensagem('Situação do ingresso atualizada.')
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }

  const excluir = async (ingresso) => {
    if (!window.confirm(`Excluir definitivamente o ingresso cancelado #${ingresso.id}?`)) return
    setProcessando(true)
    setErro('')
    try {
      await apiJson(`/api/ingressos/${ingresso.id}`, { method: 'DELETE' })
      setMensagem('Ingresso removido.')
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }

  return <section className={styles.page}>
    <header className={styles.header}><div><h1>{cliente ? 'Meus ingressos' : 'Ingressos adquiridos'}</h1><p>Aquisição simulada, com controle de capacidade, prazo e limite por cliente.</p></div></header>
    {erro && <div className={styles.error} role="alert">{erro}</div>}
    {mensagem && <Alert mensagem={mensagem} tipo="sucesso" />}
    <section className={styles.formPanel}>
      <h2>Adquirir ingresso</h2>
      <form className={styles.form} onSubmit={comprar}>
        <div className={styles.field}>
          <label htmlFor="comprar-evento">Evento</label>
          <select className={styles.input} id="comprar-evento" value={eventoId} required onChange={(e) => setEventoId(e.target.value)}>
            <option value="">Selecione um evento</option>
            {eventos.filter((e) => e.ingressosDisponiveis > 0 && new Date(e.dataHora).getTime() > Date.now()).map((e) => <option value={e.id} key={e.id}>{e.nome} — {e.ingressosDisponiveis} vaga(s)</option>)}
          </select>
        </div>
        {!cliente && <div className={styles.field}>
          <label htmlFor="comprar-cliente">Cliente</label>
          <input className={styles.input} id="comprar-cliente" type="number" min="1" required list="clientes-sugestoes" placeholder="ID do cliente" value={clienteId} onChange={(e) => setClienteId(e.target.value)} />
          <datalist id="clientes-sugestoes">{clientes.map((c) => <option value={c.id} key={c.id}>{c.nome} ({c.email})</option>)}</datalist>
          <small>Digite o ID do cliente; sugestões mostram os primeiros 100 cadastros. O backend valida a existência.</small>
        </div>}
        <div className={styles.formActions}><button className={styles.button} type="submit" disabled={processando}>{processando ? 'Registrando...' : 'Adquirir um ingresso'}</button></div>
      </form>
      <div className={styles.kpi}>Regras: capacidade máxima, compra antes do início e limite de quatro ingressos por cliente/evento.</div>
    </section>
    <div className={styles.toolbar}>
      <input className={styles.search} placeholder="Pesquisar evento ou cliente..." aria-label="Pesquisar ingressos" value={pesquisa} onChange={(e) => { setPesquisa(e.target.value); setPagina(1) }} />
      <select className={styles.select} aria-label="Filtrar status" value={filtroStatus} onChange={(e) => { setFiltroStatus(e.target.value); setPagina(1) }}>
        <option value="">Todos os status</option><option value="ATIVO">Ativos</option><option value="CANCELADO">Cancelados</option>
      </select>
      <button className={styles.secondary} type="button" onClick={() => setVersao((v) => v + 1)}>Atualizar</button>
    </div>
    {carregando ? <Loading mensagem="Carregando ingressos..." /> : <div className={styles.tableWrap}><table className={styles.table}>
      <thead><tr><th>ID</th><th>Evento</th><th>Cliente</th><th>Aquisição</th><th>Status</th>{admin && <th>Ações</th>}</tr></thead>
      <tbody>{ingressos.length === 0 ? <tr><td colSpan={admin ? 6 : 5} className={styles.empty}>Nenhum ingresso encontrado.</td></tr> : ingressos.map((i) => <tr key={i.id}>
        <td>#{i.id}</td><td>{i.eventoNome}</td><td>{i.clienteId}</td>
        <td>{new Date(i.adquiridoEm).toLocaleString('pt-BR')}</td><td>{i.status}</td>
        {admin && <td>{i.status === 'ATIVO' ? <button className={styles.danger} type="button" disabled={processando} onClick={() => atualizar(i, 'CANCELADO')}>Cancelar</button> : <><button className={styles.secondary} type="button" disabled={processando} onClick={() => atualizar(i, 'ATIVO')}>Reativar</button><button className={styles.danger} type="button" disabled={processando} onClick={() => excluir(i)}>Excluir</button></>}</td>}
      </tr>)}</tbody>
    </table></div>}
    <Paginacao page={pagina} pages={paginas} total={total} onChange={setPagina} />
  </section>
}
