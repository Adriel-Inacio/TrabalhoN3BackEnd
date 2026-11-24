import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { apiJson, requisicaoJson } from '../utils/api'
import useSaidaProtegida from '../utils/useSaidaProtegida'
import Paginacao from '../components/Paginacao'
import Loading from '../components/Loading'
import Alert from '../components/Alert'
import styles from './Cultura.module.css'

const vazio = { nome: '', descricao: '', local: '', dataHora: '', capacidadeMaxima: '50' }

export default function Eventos() {
  const { usuario } = useAuth()
  const gerencia = ['ADMIN', 'FUNCIONARIO'].includes(usuario.perfil)
  const [itens, setItens] = useState([])
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [pesquisa, setPesquisa] = useState('')
  const [sort, setSort] = useState('dataHora')
  const [ordem, setOrdem] = useState('asc')
  const [versao, setVersao] = useState(0)
  const [erro, setErro] = useState('')
  const [aviso, setAviso] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [processando, setProcessando] = useState(false)
  const [editando, setEditando] = useState(null)
  const [dados, setDados] = useState({ ...vazio })
  const [originais, setOriginais] = useState({ ...vazio })
  const pendente = editando !== null && JSON.stringify(dados) !== JSON.stringify(originais)
  useSaidaProtegida(pendente, processando)

  useEffect(() => {
    let ativo = true
    setCarregando(true)
    const params = new URLSearchParams({ page, perPage: 10, q: pesquisa, sort, ordem })
    apiJson(`/api/eventos?${params}`)
      .then((resultado) => {
        if (!ativo) return
        setItens(resultado.items)
        setPages(resultado.pages)
        setTotal(resultado.total)
        setErro('')
      })
      .catch((e) => { if (ativo) setErro(e.message) })
      .finally(() => { if (ativo) setCarregando(false) })
    return () => { ativo = false }
  }, [page, pesquisa, sort, ordem, versao])

  const atualizarCampo = (campo, valor) => setDados((anterior) => ({ ...anterior, [campo]: valor }))
  const iniciarCadastro = () => {
    if (pendente && !window.confirm('Descartar alterações não salvas?')) return
    setDados({ ...vazio })
    setOriginais({ ...vazio })
    setEditando('novo')
    setAviso('')
  }
  const iniciarEdicao = (evento) => {
    if (pendente && !window.confirm('Descartar alterações não salvas?')) return
    const form = { nome: evento.nome, descricao: evento.descricao, local: evento.local,
      dataHora: evento.dataHora.slice(0, 16), capacidadeMaxima: String(evento.capacidadeMaxima) }
    setDados(form)
    setOriginais({ ...form })
    setEditando(evento.id)
    setAviso('')
  }
  const salvar = async (e) => {
    e.preventDefault()
    if (processando) return
    setProcessando(true)
    setErro('')
    setAviso('')
    try {
      const corpo = { ...dados, capacidadeMaxima: Number(dados.capacidadeMaxima) }
      const novo = editando === 'novo'
      await apiJson(novo ? '/api/eventos' : `/api/eventos/${editando}`, requisicaoJson(novo ? 'POST' : 'PUT', corpo))
      setAviso(novo ? 'Evento cadastrado.' : 'Evento atualizado.')
      setEditando(null)
      setVersao((v) => v + 1)
    } catch (falha) {
      setErro(falha.message)
    } finally {
      setProcessando(false)
    }
  }
  const excluir = async (evento) => {
    if (pendente) return setErro('Salve ou descarte as alterações antes de excluir.')
    if (!window.confirm(`Excluir o evento ${evento.nome}? Somente eventos sem ingressos podem ser removidos.`)) return
    setProcessando(true)
    setErro('')
    try {
      await apiJson(`/api/eventos/${evento.id}`, { method: 'DELETE' })
      setAviso('Evento excluído.')
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }

  return <section className={styles.page}>
    <header className={styles.header}>
      <div><h1>Eventos culturais</h1><p>Consulte a programação, a capacidade e os ingressos disponíveis.</p></div>
      {gerencia && <button className={styles.button} type="button" onClick={iniciarCadastro}>Cadastrar evento</button>}
    </header>
    {erro && <div className={styles.error} role="alert">{erro}</div>}
    {aviso && <Alert mensagem={aviso} tipo="sucesso" />}
    {editando !== null && gerencia && <section className={styles.formPanel}>
      <h2>{editando === 'novo' ? 'Novo evento' : `Editar evento #${editando}`}</h2>
      <form className={styles.form} onSubmit={salvar}>
        <div className={styles.field}><label htmlFor="evento-nome">Nome</label><input className={styles.input} id="evento-nome" required maxLength={120} value={dados.nome} onChange={(e) => atualizarCampo('nome', e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="evento-local">Local</label><input className={styles.input} id="evento-local" required maxLength={200} value={dados.local} onChange={(e) => atualizarCampo('local', e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="evento-data">Data e horário</label><input className={styles.input} id="evento-data" type="datetime-local" required value={dados.dataHora} onChange={(e) => atualizarCampo('dataHora', e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="evento-capacidade">Capacidade máxima</label><input className={styles.input} id="evento-capacidade" type="number" min="1" step="1" required value={dados.capacidadeMaxima} onChange={(e) => atualizarCampo('capacidadeMaxima', e.target.value)} /></div>
        <div className={`${styles.field} ${styles.full}`}><label htmlFor="evento-descricao">Descrição</label><textarea className={styles.textarea} id="evento-descricao" required maxLength={1000} value={dados.descricao} onChange={(e) => atualizarCampo('descricao', e.target.value)} /></div>
        <div className={styles.formActions}><button className={styles.secondary} type="button" onClick={() => { if (!pendente || window.confirm('Descartar alterações?')) setEditando(null) }} disabled={processando}>Cancelar</button><button className={styles.button} type="submit" disabled={processando || (editando !== 'novo' && !pendente)}>{processando ? 'Salvando...' : 'Salvar evento'}</button></div>
      </form>
    </section>}
    <div className={styles.toolbar}>
      <input className={styles.search} aria-label="Pesquisar evento" placeholder="Pesquisar evento ou local..." value={pesquisa} onChange={(e) => { setPesquisa(e.target.value); setPage(1) }} />
      <select className={styles.select} aria-label="Ordenação" value={`${sort}:${ordem}`} onChange={(e) => { const [c, o] = e.target.value.split(':'); setSort(c); setOrdem(o); setPage(1) }}>
        <option value="dataHora:asc">Data mais próxima</option><option value="dataHora:desc">Data mais distante</option>
        <option value="nome:asc">Nome A–Z</option><option value="capacidadeMaxima:desc">Maior capacidade</option>
      </select>
      <button className={styles.secondary} type="button" onClick={() => setVersao((v) => v + 1)} disabled={carregando}>Atualizar</button>
    </div>
    {carregando ? <Loading mensagem="Carregando eventos..." /> : itens.length === 0 ? <div className={styles.empty}>Nenhum evento encontrado.</div> : <div className={styles.cards}>
      {itens.map((item) => <article className={styles.card} key={item.id}>
        <h3>{item.nome}</h3><p>{item.descricao}</p><p><strong>Local:</strong> {item.local}</p>
        <p><strong>Data:</strong> {new Date(item.dataHora).toLocaleString('pt-BR')}</p>
        <p><strong>Capacidade:</strong> {item.capacidadeMaxima}</p>
        <p className={item.ingressosDisponiveis ? styles.success : styles.warning}><strong>Vagas disponíveis:</strong> {item.ingressosDisponiveis}</p>
        {gerencia && <div className={styles.actions}>
          <button className={styles.secondary} type="button" disabled={processando} onClick={() => iniciarEdicao(item)}>Editar</button>
          {usuario.perfil === 'ADMIN' && <button className={styles.danger} type="button" disabled={processando} onClick={() => excluir(item)}>Excluir</button>}
        </div>}
      </article>)}
    </div>}
    <Paginacao page={page} pages={pages} total={total} onChange={setPage} />
  </section>
}
