
import { useEffect, useState } from 'react'
import styles from './Alert.module.css'

export default function Alert({ mensagem, tipo }) {
  const [visivel, setVisivel] = useState(Boolean(mensagem))
  const [saindo, setSaindo] = useState(false)

  const sucesso = tipo === 'sucesso'

  useEffect(() => {
    if (!mensagem) {
      setVisivel(false)
      setSaindo(false)
      return
    }

    setVisivel(true)
    setSaindo(false)

    const tempoExibicao = setTimeout(() => {
      setSaindo(true)
    }, 5000)

    return () => clearTimeout(tempoExibicao)
  }, [mensagem, tipo])

  const fecharNotificacao = () => {
    setSaindo(true)
  }

  const finalizarAnimacao = () => {
    if (saindo) {
      setVisivel(false)
    }
  }

  if (!mensagem || !visivel) {
    return null
  }

  return (
    <div
      className={`${styles.alert} ${
        sucesso ? styles.sucesso : styles.erro
      } ${saindo ? styles.saida : styles.entrada}`}
      role={sucesso ? 'status' : 'alert'}
      onAnimationEnd={finalizarAnimacao}
    >
      <span aria-hidden="true">
        {sucesso ? '✓' : '⚠'}
      </span>

      <span className={styles.mensagem}>
        {mensagem}
      </span>

      <button
        type="button"
        className={styles.fecharButton}
        onClick={fecharNotificacao}
        disabled={saindo}
        aria-label="Fechar notificação"
      >
        ×
      </button>
    </div>
  )
}
