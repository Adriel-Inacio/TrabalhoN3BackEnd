import { useState } from 'react'
import { apiJson, requisicaoJson } from '../utils/api'
import styles from './EntityForm.module.css'

export default function WorkerAccess({ funcionario, onUpdate }) {
  const [senha, setSenha] = useState('')
  const [ativo, setAtivo] = useState(Boolean(funcionario.ativo))
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')

  const salvar = async (evento) => {
    evento.preventDefault()
    if (salvando) return
    setSalvando(true)
    setErro('')
    setSucesso('')
    try {
      const resposta = await apiJson(`/api/funcionarios/${funcionario.id}/acesso`, requisicaoJson('PUT', { senha: senha || undefined, ativo }))
      setSenha('')
      setSucesso('Credenciais e acesso atualizados.')
      onUpdate(resposta.funcionario)
    } catch (falha) {
      setErro(falha.message)
    } finally {
      setSalvando(false)
    }
  }

  return <div className={`${styles.full} ${styles.container}`}>
    <h3>Acesso ao sistema</h3>
    {erro && <p role="alert" style={{ color: '#b91c1c' }}>{erro}</p>}
    {sucesso && <p role="status" style={{ color: '#15803d' }}>{sucesso}</p>}
    <form onSubmit={salvar} className={styles.form}>
      <div className={styles.field}><label htmlFor={`funcionario-senha-${funcionario.id}`}>Nova senha (opcional)</label><input id={`funcionario-senha-${funcionario.id}`} type="password" autoComplete="new-password" minLength={10} maxLength={128} placeholder="Deixe em branco para manter" value={senha} onChange={(e) => setSenha(e.target.value)} disabled={salvando} /></div>
      <div className={styles.field}><label htmlFor={`funcionario-ativo-${funcionario.id}`}>Permissão de acesso</label><select id={`funcionario-ativo-${funcionario.id}`} value={String(ativo)} onChange={(e) => setAtivo(e.target.value === 'true')} disabled={salvando}><option value="true">Acesso ativo</option><option value="false">Acesso desativado</option></select></div>
      <div className={styles.actions}><button type="submit" disabled={salvando}>{salvando ? 'Salvando...' : 'Salvar acesso'}</button></div>
    </form>
  </div>
}
