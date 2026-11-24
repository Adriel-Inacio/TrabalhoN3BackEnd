import { useState } from 'react'

import {
  formatarTelefone,
  formatarCpf,
  somenteNumeros
} from '../utils/mascaras'

import Alert from '../components/Alert'
import { apiFetch } from '../utils/api'

import styles from "./RegisterWorker.module.css"

export default function Insert(){
  const [status, setStatus] = useState('')
  const [tipoStatus, setTipoStatus] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [alertId, setAlertId] = useState(0)
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [telefone, setTelefone] = useState('')
  const [cpf, setCpf] = useState('')
  const [senha, setSenha] = useState('')

  const updateMask = (event, formatar, atualizarEstado) => {
    const input = event.target
    const valor = input.value
    const posicao = input.selectionStart ?? valor.length

    const digitosAntes = valor.slice(0, posicao).replace(/\D/g, '').length

    const formatado = formatar(valor)
    atualizarEstado(formatado)

    requestAnimationFrame(() => {
      const quantidadeTotal = formatado.replace(/\D/g, '').length

      if (quantidadeTotal === 0) {
        input.setSelectionRange(0, 0)
        return
      }

      let novaPosicao = 0
      let encontrados = 0

      while (
        novaPosicao < formatado.length &&
        encontrados < digitosAntes
      ) {
        if (/\d/.test(formatado[novaPosicao])) {
          encontrados++
        }
        novaPosicao++
      }

      if (posicao === valor.length) {
        novaPosicao = formatado.length
      }

      input.setSelectionRange(novaPosicao, novaPosicao)
    })
  }

  const tratarBackspace = (event, valor, formatar, atualizarEstado) => {
  if (event.key !== 'Backspace') return

  const input = event.currentTarget
  const posicao = input.selectionStart
  const fim = input.selectionEnd

  if (posicao === null || posicao !== fim || posicao === 0) {
    return
  }

  if (/\d/.test(valor[posicao - 1])) {
    return
  }

  event.preventDefault()

  const antes = valor.slice(0, posicao)
  const depois = valor.slice(posicao)

  const indiceDigito = antes.search(/\d(?=\D*$)/)

  if (indiceDigito === -1) return

  const novoValor =
    valor.slice(0, indiceDigito) +
    valor.slice(indiceDigito + 1)

  const formatado = formatar(novoValor)
  atualizarEstado(formatado)

  requestAnimationFrame(() => {
    const digitosAntes = valor
      .slice(0, indiceDigito)
      .replace(/\D/g, '').length

    let novaPosicao = 0
    let encontrados = 0

    while (
      novaPosicao < formatado.length &&
      encontrados < digitosAntes
    ) {
      if (/\d/.test(formatado[novaPosicao])) {
        encontrados++
      }

      novaPosicao++
    }

    input.setSelectionRange(novaPosicao, novaPosicao)
  })
}

  const PostTreat = (event) => {
    event.preventDefault()

    if (salvando) return

    setSalvando(true)

    const dataToSend = {
      nome,
      email,
      telefone: somenteNumeros(telefone),
      cpf: somenteNumeros(cpf),
      senha
    }

    apiFetch('/api/funcionarios/novo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dataToSend)
    })
    .then((res) => {
      console.log("Status HTTP:", res.status)
      return res.json().then((data) => {
        if(!res.ok) {
          throw new Error(
            data.erro || "Erro ao cadastar funcionário."
          )
        }
        return data
      })
    })
    .then((data) => {
      setStatus('Funcionário cadastrado com sucesso!')
      setTipoStatus('sucesso')
      setAlertId((atual) => atual + 1)

      setNome('')
      setEmail('')
      setTelefone('')
      setCpf('')
      setSenha('')
    })
    .catch((erro) => {
      setStatus(erro.message)
      setTipoStatus('erro')
    })
    .finally(() => {
      setSalvando(false)
    })
  }

  return (
    <section className={styles.container}>
      <header className={styles.header}>
          <h2>Cadastrar funcionário</h2>
          <p>Preench os dados do novo funcionário.</p>
      </header>

      <Alert
        key={alertId}
        mensagem={status}
        tipo={tipoStatus}
      />

      <form onSubmit={PostTreat} className={styles.form}>
        <div className={styles.field}>
          <label htmlFor="nome">Nome Completo</label>
          <input id="nome" type="text" value={nome} onChange={(e) => setNome(e.target.value)} required/>
        </div>

        <div className={styles.field}>
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required/>
        </div>

        <div className={styles.field}>
          <label htmlFor="telefone">Telefone</label>
          <input
            id="telefone"
            type="tel"
            placeholder='(00)00000-0000'
            maxLength={14} value={telefone}
            onChange={(e) => updateMask(
              e,
              formatarTelefone,
              setTelefone
            )}
            onKeyDown={(e) => tratarBackspace(
              e,
              telefone,
              formatarTelefone,
              setTelefone
            )}
            required/>
        </div>

        <div className={styles.field}>
          <label htmlFor="cpf">CPF</label>
          <input
            id="cpf"
            type="text"
            placeholder='000.000.000-00'
            maxLength={14}
            value={cpf}
            onChange={(e) => updateMask(
              e,
              formatarCpf,
              setCpf
            )}
            onKeyDown={(e) => tratarBackspace(
              e,
              cpf,
              formatarCpf,
              setCpf
            )}
            required/>
        </div>

        <div className={styles.field}>
          <label htmlFor="senha-funcionario">Senha inicial de acesso</label>
          <input id="senha-funcionario" type="password" autoComplete="new-password" minLength={10} maxLength={128} value={senha} disabled={salvando} onChange={(e) => setSenha(e.target.value)} required />
        </div>

        <div className={styles.actions}>
          <button
            type="submit"
            disabled={salvando}
            aria-busy={salvando}
          >
            {salvando ? (
              <>
                <span
                  className={styles.buttonSpinner}
                  aria-hidden="true"
                />
                Salvando...
              </>
            ) : (
              'Salvar funcionário'
            )}
          </button>
        </div>
      </form>
    </section>
  )
}