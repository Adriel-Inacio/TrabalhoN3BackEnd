import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { apiJson, requisicaoJson } from '../utils/api'
import { formatarTelefone, somenteNumeros } from '../utils/mascaras'
import useSaidaProtegida from '../utils/useSaidaProtegida'
import Paginacao from '../components/Paginacao'
import Loading from '../components/Loading'
import Alert from '../components/Alert'
import styles from './Cultura.module.css'

const inicial = { nome: '', email: '', telefone: '', senha: '' }

export default function Clientes() {
  const { usuario } = useAuth()
  const admin = usuario.perfil === 'ADMIN'
  const [itens, setItens] = useState([])
  const [pagina, setPagina] = useState(1)
  const [paginas, setPaginas] = useState(1)
  const [total, setTotal] = useState(0)
  const [pesquisa, setPesquisa] = useState('')
  const [versao, setVersao] = useState(0)
  const [editando, setEditando] = useState(null)
  const [dados, setDados] = useState({ ...inicial })
  const [originais, setOriginais] = useState({ ...inicial })
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [processando, setProcessando] = useState(false)
  const pendente = editando !== null && JSON.stringify(dados) !== JSON.stringify(originais)
  useSaidaProtegida(pendente, processando)

  useEffect(() => {
    let ativo = true
    setCarregando(true)
    const params = new URLSearchParams({ page: pagina, perPage: 10, q: pesquisa, sort: 'nome' })
    apiJson(`/api/clientes?${params}`).then((resposta) => {
      if (!ativo) return
      setItens(resposta.items)
      setPaginas(resposta.pages)
      setTotal(resposta.total)
      setErro('')
    }).catch((falha) => { if (ativo) setErro(falha.message) })
      .finally(() => { if (ativo) setCarregando(false) })
    return () => { ativo = false }
  }, [pagina, pesquisa, versao])

  const alterar = (campo, valor) => setDados((antigo) => ({ ...antigo, [campo]: valor }))
  const novo = () => {
    if (pendente && !window.confirm('Descartar alterações?')) return
    setDados({ ...inicial }); setOriginais({ ...inicial }); setEditando('novo'); setSucesso('')
  }
  const editar = (cliente) => {
    if (pendente && !window.confirm('Descartar alterações?')) return
    const form = { nome: cliente.nome, email: cliente.email, telefone: formatarTelefone(cliente.telefone), senha: '' }
    setDados(form); setOriginais({ ...form }); setEditando(cliente.id); setSucesso('')
  }
  const salvar = async (e) => {
    e.preventDefault()
    if (processando) return
    setErro(''); setSucesso(''); setProcessando(true)
    try {
      const corpo = { nome: dados.nome, email: dados.email, telefone: somenteNumeros(dados.telefone) }
      if (dados.senha) corpo.senha = dados.senha
      const cadastro = editando === 'novo'
      await apiJson(cadastro ? '/api/clientes' : `/api/clientes/${editando}`, requisicaoJson(cadastro ? 'POST' : 'PUT', corpo))
      setSucesso(cadastro ? 'Cliente cadastrado.' : 'Cliente atualizado.')
      setEditando(null)
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }
  const excluir = async (cliente) => {
    if (!window.confirm(`Excluir ${cliente.nome}? Clientes com ingressos não podem ser removidos.`)) return
    setProcessando(true)
    try {
      await apiJson(`/api/clientes/${cliente.id}`, { method: 'DELETE' })
      setSucesso('Cliente excluído.')
      setVersao((v) => v + 1)
    } catch (falha) { setErro(falha.message) }
    finally { setProcessando(false) }
  }

  return <section className={styles.page}>
    <header className={styles.header}><div><h1>Clientes</h1><p>{admin ? 'Gerencie os compradores e suas contas.' : 'Consulte os compradores cadastrados.'}</p></div>{admin && <button type="button" className={styles.button} onClick={novo}>Cadastrar cliente</button>}</header>
    {erro && <div className={styles.error} role="alert">{erro}</div>}
    {sucesso && <Alert tipo="sucesso" mensagem={sucesso} />}
    {admin && editando !== null && <section className={styles.formPanel}><h2>{editando === 'novo' ? 'Novo cliente' : `Editar cliente #${editando}`}</h2>
      <form className={styles.form} onSubmit={salvar}>
        <div className={styles.field}><label htmlFor="cliente-nome">Nome</label><input className={styles.input} id="cliente-nome" value={dados.nome} required maxLength={80} onChange={(e) => alterar('nome', e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="cliente-email">E-mail</label><input className={styles.input} id="cliente-email" type="email" required maxLength={80} value={dados.email} onChange={(e) => alterar('email', e.target.value)} /></div>
        <div className={styles.field}><label htmlFor="cliente-telefone">Telefone</label><input className={styles.input} id="cliente-telefone" type="tel" required value={dados.telefone} onChange={(e) => alterar('telefone', formatarTelefone(e.target.value))} /></div>
        <div className={styles.field}><label htmlFor="cliente-senha">{editando === 'novo' ? 'Senha inicial' : 'Nova senha (opcional)'}</label><input className={styles.input} id="cliente-senha" type="password" autoComplete="new-password" minLength={10} maxLength={128} required={editando === 'novo'} value={dados.senha} onChange={(e) => alterar('senha', e.target.value)} /></div>
        <div className={styles.formActions}><button className={styles.secondary} type="button" onClick={() => { if (!pendente || window.confirm('Descartar alterações?')) setEditando(null) }}>Cancelar</button><button className={styles.button} type="submit" disabled={processando || (editando !== 'novo' && !pendente)}>{processando ? 'Salvando...' : 'Salvar cliente'}</button></div>
      </form>
    </section>}
    <div className={styles.toolbar}><input className={styles.search} value={pesquisa} placeholder="Pesquisar nome ou e-mail..." aria-label="Pesquisar clientes" onChange={(e) => { setPesquisa(e.target.value); setPagina(1) }} /><button className={styles.secondary} type="button" onClick={() => setVersao((v) => v + 1)}>Atualizar</button></div>
    {carregando ? <Loading mensagem="Carregando clientes..." /> : <div className={styles.tableWrap}><table className={styles.table}>
      <thead><tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Telefone</th>{admin && <th>Ações</th>}</tr></thead>
      <tbody>{itens.length === 0 ? <tr><td className={styles.empty} colSpan={admin ? 5 : 4}>Nenhum cliente encontrado.</td></tr> : itens.map((c) => <tr key={c.id}><td>{c.id}</td><td>{c.nome}</td><td>{c.email}</td><td>{formatarTelefone(c.telefone)}</td>{admin && <td><button className={styles.secondary} type="button" disabled={processando} onClick={() => editar(c)}>Editar</button><button className={styles.danger} type="button" disabled={processando} onClick={() => excluir(c)}>Excluir</button></td>}</tr>)}</tbody>
    </table></div>}
    <Paginacao page={pagina} pages={paginas} total={total} onChange={setPagina} />
  </section>
}
