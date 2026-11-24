import styles from '../pages/Cultura.module.css'

export default function Paginacao({ page, pages, total, onChange }) {
  return <div className={styles.pagination}>
    <span>{total} registro(s) · Página {page} de {Math.max(pages, 1)}</span>
    <div className={styles.actions}>
      <button className={styles.secondary} type="button" disabled={page <= 1} onClick={() => onChange(page - 1)}>Anterior</button>
      <button className={styles.secondary} type="button" disabled={page >= pages} onClick={() => onChange(page + 1)}>Próxima</button>
    </div>
  </div>
}
