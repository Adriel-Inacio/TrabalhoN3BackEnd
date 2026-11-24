import { NavLink, Outlet } from 'react-router-dom'
import styles from "./Worker.module.css"

export default function Funcionario() {
    return (
        <section className={styles.worker}>
            <header className={styles.header}>
                <h1>Funcionarios</h1>
                <nav className={styles.nav}>
                    <NavLink 
                        to="/funcionarios"
                        end
                        className={({ isActive }) => 
                            isActive
                                ? `${styles.link} ${styles.active}`
                                : styles.link
                        }
                    >
                        Lista de Funcionarios
                    </NavLink>
                    
                    <NavLink
                        to="/funcionarios/novo"
                        end
                        className={({ isActive }) => 
                            isActive
                                ? `${styles.link} ${styles.active}`
                                : styles.link
                        }
                    >
                        Cadastrar Funcionario
                    </NavLink>
                </nav>
            </header>
            
            <div className={styles.content}>
                <Outlet />
            </div>
        </section>
    )
}

