export const somenteNumeros = (valor) => {
  return String(valor ?? '').replace(/\D/g, '')
}

export const formatarTelefone = (valor) => {
  const numeros = somenteNumeros(valor).slice(0, 11)

  if (numeros.length === 0) {
    return ''
  }

  if (numeros.length <= 2) {
    return `(${numeros}`
  }

  if (numeros.length <= 6) {
    return `(${numeros.slice(0, 2)})${numeros.slice(2)}`
  }

  if (numeros.length <= 10) {
    return `(${numeros.slice(0, 2)})${numeros.slice(2, 6)}-${numeros.slice(6)}`
  }

  return `(${numeros.slice(0, 2)})${numeros.slice(2, 7)}-${numeros.slice(7)}`
}

export const formatarCpf = (valor) => {
  const numeros = somenteNumeros(valor).slice(0, 11)

  return numeros
    .replace(/^(\d{3})(\d)/, '$1.$2')
    .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3-$4')
}