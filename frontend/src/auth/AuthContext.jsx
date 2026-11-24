import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { apiJson, definirCsrfToken, requisicaoJson } from '../utils/api'

const Contexto = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    let ativo = true
    apiJson('/api/auth/me')
      .then((dados) => {
        if (ativo) {
          definirCsrfToken(dados.csrf_token)
          setUsuario(dados.usuario)
        }
      })
      .catch(() => {
        if (ativo) {
          definirCsrfToken('')
          setUsuario(null)
        }
      })
      .finally(() => { if (ativo) setCarregando(false) })
    const encerrar = () => {
      definirCsrfToken('')
      setUsuario(null)
    }
    window.addEventListener('sysstock:unauthorized', encerrar)
    return () => {
      ativo = false
      window.removeEventListener('sysstock:unauthorized', encerrar)
    }
  }, [])

  const login = async (email, senha) => {
    const dados = await apiJson('/api/auth/login', requisicaoJson('POST', { email, senha }))
    definirCsrfToken(dados.csrf_token)
    setUsuario(dados.usuario)
    return dados.usuario
  }

  const logout = async () => {
    try {
      await apiJson('/api/auth/logout', { method: 'POST' })
    } finally {
      definirCsrfToken('')
      setUsuario(null)
    }
  }

  const valor = useMemo(() => ({ usuario, carregando, login, logout }), [usuario, carregando])
  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>
}

export function useAuth() {
  const contexto = useContext(Contexto)
  if (!contexto) throw new Error('Autenticação não inicializada.')
  return contexto
}
