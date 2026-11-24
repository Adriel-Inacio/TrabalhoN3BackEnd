import { useEffect } from 'react'
import { useBlocker } from 'react-router-dom'

export default function useSaidaProtegida(alteracoesPendentes, processando = false) {
  const blocker = useBlocker(({ currentLocation, nextLocation }) => {
    const mudouEndereco =
      currentLocation.pathname !== nextLocation.pathname ||
      currentLocation.search !== nextLocation.search ||
      currentLocation.hash !== nextLocation.hash

    return mudouEndereco && (alteracoesPendentes || processando)
  })

  useEffect(() => {
    if (blocker.state !== 'blocked') return

    if (processando) {
      blocker.reset()
      return
    }

    if (window.confirm('Existem alterações não salvas. Deseja descartá-las e sair desta página?')) {
      blocker.proceed()
    } else {
      blocker.reset()
    }
  }, [blocker, processando])

  useEffect(() => {
    if (!alteracoesPendentes && !processando) return

    const confirmarSaida = (evento) => {
      evento.preventDefault()
      evento.returnValue = ''
    }

    window.addEventListener('beforeunload', confirmarSaida)
    return () => window.removeEventListener('beforeunload', confirmarSaida)
  }, [alteracoesPendentes, processando])
}
