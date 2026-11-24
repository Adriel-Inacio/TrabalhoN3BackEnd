
import styles from './Loading.module.css'

export default function Loading({
  mensagem = 'Carregando...'
}) {
  return (
    <div
      className={styles.loading}
      role="status"
      aria-live="polite"
    >
      <span
        className={styles.spinner}
        aria-hidden="true"
      />

      <span className={styles.mensagem}>
        {mensagem}
      </span>
    </div>
  )
}
