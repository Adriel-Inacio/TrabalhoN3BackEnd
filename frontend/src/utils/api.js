let csrfToken = ''

export function definirCsrfToken(token) {
  csrfToken = token || ''
}

export async function apiFetch(url, options = {}) {
  const metodo = (options.method || 'GET').toUpperCase()
  const headers = new Headers(options.headers || {})
  if (!['GET', 'HEAD', 'OPTIONS'].includes(metodo) && csrfToken && !url.endsWith('/auth/login') && !url.endsWith('/auth/cadastro')) {
    headers.set('X-CSRF-Token', csrfToken)
  }
  let resposta
  try {
    resposta = await fetch(url, { ...options, credentials: 'same-origin', headers })
  } catch (erro) {
    if (erro.name === 'AbortError') throw erro
    throw new Error('Não foi possível conectar ao servidor. Verifique se a API está funcionando.')
  }
  if (resposta.status === 401 && !url.endsWith('/auth/login') && !url.endsWith('/auth/me')) {
    window.dispatchEvent(new Event('sysstock:unauthorized'))
  }
  return resposta
}

export async function apiJson(url, options = {}) {
  const resposta = await apiFetch(url, options)
  let dados = null
  const texto = await resposta.text()
  if (texto.trim()) {
    try {
      dados = JSON.parse(texto)
    } catch {
      throw new Error('A API retornou uma resposta inválida.')
    }
  }
  if (!resposta.ok) {
    const erro = new Error(dados?.erro || dados?.message || `Erro HTTP ${resposta.status}.`)
    erro.status = resposta.status
    throw erro
  }
  return dados
}

export function requisicaoJson(metodo, corpo) {
  return {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo)
  }
}
