import { useEffect, useState, useRef, Fragment } from 'react'
import { useBlocker } from 'react-router-dom'
import { apiFetch } from '../utils/api'
import WorkerAccess from './WorkerAccess'

import {
  formatarTelefone,
  formatarCpf,
  somenteNumeros
} from '../utils/mascaras'

import Alert from '../components/Alert'
import Loading from '../components/Loading'

import styles from "./SelectWorker.module.css"

export default function Select(){
  const [status, setStatus] = useState('carregando')
  const [itens, setItens] = useState([])
  const [erro, setErro] = useState(null)
  const [pesquisa, setPesquisa] = useState("")
  const [funcionarioAberto, setFuncionarioAberto] = useState(null)
  const [funcionarioEditando, setFuncionarioEditando] = useState(null)
  const [salvando, setSalvando] = useState(null)
  const [mensagemEdicao, setMensagemEdicao] = useState("")
  const [tipoMensagem, setTipoMensagem] = useState("")
  const [alertId, setAlertId] = useState(0)
  const [funcionarioExcluindo, setFuncionarioExcluindo] = useState(null);
  const [excluindo, setExcluindo] = useState(false);
  const [sincronizando, setSincronizando] = useState(false)
  const [erroSincronizacao, setErroSincronizacao] = useState("")

  const requisicaoAtual = useRef(null)

  const processando = Boolean(salvando) || excluindo ||sincronizando

  const [dadosEdicao, setDadosEdicao] = useState({
    nome: "",
    email: "",
    telefone: "",
    cpf: ""
  })

  const [dadosOriginais, setDadosOriginais] = useState({
    nome: "",
    email: "",
    telefone: "",
    cpf: ""
  })

  const temAlteracoes =
    dadosEdicao.nome !== dadosOriginais.nome ||
    dadosEdicao.email !== dadosOriginais.email ||
    dadosEdicao.telefone !== dadosOriginais.telefone ||
    dadosEdicao.cpf !== dadosOriginais.cpf

  const campoFoiAlterado = (campo) => {
    return dadosEdicao[campo] !== dadosOriginais[campo]
  }

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) => {
      const existemAlteracoesPendentes =
        funcionarioEditando !== null && temAlteracoes

      const operacaoEmAndamento =
        Boolean(salvando) || excluindo || sincronizando

      const mudouPagina =
        currentLocation.pathname !== nextLocation.pathname

      const mudouParametros =
        currentLocation.search !== nextLocation.search

      const mudouHash =
        currentLocation.hash !== nextLocation.hash

      const mudouEndereco =
        mudouPagina || mudouParametros || mudouHash

      return (
        mudouEndereco &&
        (existemAlteracoesPendentes || operacaoEmAndamento)
      )
    }
  )

  useEffect(() => {
    if (blocker.state !== "blocked") return

    if (processando) {
      blocker.reset()
      return
    }

    const confirmou = window.confirm(
      "Você possui alterações não salvas neste funcionário. " +
      "Deseja descartá-las e sair desta página?"
    )

    if (confirmou) {
      blocker.proceed()
    } else {
      blocker.reset()
    }
  }, [blocker, processando])

  useEffect(() => {
    const existemAlteracoesPendentes =
      funcionarioEditando !== null && temAlteracoes

    const operacaoEmAndamento =
      Boolean(salvando) || excluindo || sincronizando

    if (!existemAlteracoesPendentes && !operacaoEmAndamento) {
      return
    }

    const confirmarSaida = (event) => {
      event.preventDefault()
      event.returnValue = ""
    }

    window.addEventListener("beforeunload", confirmarSaida)

    return () => {
      window.removeEventListener("beforeunload", confirmarSaida)
    }
  }, [
    funcionarioEditando,
    temAlteracoes,
    salvando,
    excluindo,
    sincronizando
  ])

  const carregarFuncionarios = (manterTabela = false) => {
    requisicaoAtual.current?.abort()

    const controller = new AbortController()
    requisicaoAtual.current = controller

    if (manterTabela && status === 'sucesso') {
      setSincronizando(true)
    } else {
      setStatus('carregando')
      setSincronizando(false)
    }

    setErro(null)
    setErroSincronizacao("")

    return apiFetch('/api/dados', {
      signal: controller.signal
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(
            'Não foi possível consultar os funcionários.'
          )
        }

        return res.json()
      })
      .then((data) => {
        if (controller.signal.aborted) return

        if (!Array.isArray(data)) {
          throw new Error(
            'A API retornou dados em um formato inesperado.'
          )
        }

        setItens(data)
        setStatus('sucesso')
      })   
      .catch((erro) => {
        if (controller.signal.aborted) return

        if (manterTabela && status === 'sucesso') {
          setErroSincronizacao(
            erro.message ||
            "Não foi possível atualizar a lista de funcionários."
          )
        } else {
          setErro(erro.message)
          setStatus('erro')
        }
      })
      .finally(() => {
        if (requisicaoAtual.current === controller) {
          requisicaoAtual.current = null
          setSincronizando(false)
        }
      })
  }

  useEffect(() => {
    carregarFuncionarios()

    return () => {
      requisicaoAtual.current?.abort()
    }
  }, [])

  const funcionariosFiltrados = itens.filter((funcionario) => {
    const termo = pesquisa.toLowerCase().trim()

    return (
      String(funcionario.id).includes(termo) ||
      funcionario.nome.toLowerCase().includes(termo) ||
      funcionario.email.toLowerCase().includes(termo)
    )
  })
  .sort((a, b) => Number(a.id) - Number(b.id))

  const alternarDetalhes = (id) => {
    if (processando) return

    if (funcionarioEditando !== null && temAlteracoes) {
      const confirmou = window.confirm(
        "Existem alterações não salvas. Deseja descartá-las?"
      )

      if (!confirmou) return
    }

    setFuncionarioAberto((atual) =>
      atual === id ? null : id
    )

    setFuncionarioEditando(null)
    setFuncionarioExcluindo(null)
  }

  const iniciarEdicao = (funcionario) => {
    if (processando) return

    const dadosIniciais = {
      nome: funcionario.nome,
      email: funcionario.email,
      telefone: formatarTelefone(funcionario.telefone ?? ""),
      cpf: formatarCpf(funcionario.cpf ?? "")
    }

    setFuncionarioEditando(funcionario.id)

    setDadosEdicao(dadosIniciais)
    setDadosOriginais({ ...dadosIniciais })
  }

  const cancelarEdicao = () => {
    if (processando) return

    if (temAlteracoes) {
      const confirmou = window.confirm(
        "Existem alterações não salvas. Deseja descartá-las?"
      )

      if (!confirmou) return
    }

    setFuncionarioEditando(null)
  }

  const restaurarEdicao = () => {
    if (processando || !temAlteracoes) return

    setDadosEdicao({ ...dadosOriginais })
  }

  const salvarEdicao = async (id) => {
    if (processando || !temAlteracoes) return

    setSalvando(true)
    setMensagemEdicao("")
    setTipoMensagem("")

    try {
      const resposta = await apiFetch(`/api/funcionarios/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ...dadosEdicao,
          telefone: somenteNumeros(dadosEdicao.telefone),
          cpf: somenteNumeros(dadosEdicao.cpf)
        })
      })

      const dados = await resposta.json()

      if(!resposta.ok){
        throw new Error(
          dados.erro || "Erro ao atualizar funcionário."
        )
      }
      
      setItens((atual) =>
        atual.map((funcionario) =>
          funcionario.id === id
            ? dados.funcionario
            : funcionario
        )
      )

      setFuncionarioEditando(null)

      setMensagemEdicao("Funcionário atualizado com sucesso!")
      setTipoMensagem("sucesso")
      setAlertId((atual) => atual + 1)

      await carregarFuncionarios(true)

    } catch (erro) {
      setMensagemEdicao(erro.message)
      setTipoMensagem("erro")
      setAlertId((atual) => atual + 1)

    } finally {
      setSalvando(false)
    }
  }

  const excluirFuncionario = async (id) => {
  if (processando) return;

  setExcluindo(true);
  setMensagemEdicao("");
  setTipoMensagem("")

  try {
    const resposta = await apiFetch(`/api/funcionarios/${id}`, {
      method: "DELETE"
    });

    const dados = await resposta.json();

    if (!resposta.ok) {
      throw new Error(
        dados.erro || "Erro ao excluir funcionário."
      );
    }

    setItens((atual) =>
      atual.filter((funcionario) => funcionario.id !== id)
    )

    setFuncionarioAberto(null)
    setFuncionarioEditando(null)
    setFuncionarioExcluindo(null)

    setMensagemEdicao(
      dados.message || "Funcionário excluído com sucesso!"
    )
    setTipoMensagem("sucesso")
    setAlertId((atual) => atual + 1)

    await carregarFuncionarios(true)

    } catch (erro) {
      setMensagemEdicao(erro.message);
      setFuncionarioExcluindo(null);
      setTipoMensagem("erro")
      setAlertId((atual) => atual + 1)

    } finally {
      setExcluindo(false);
    }
  };

  return (
    <section className={styles.container}>

      <Alert
      key={alertId}
        mensagem={mensagemEdicao}
        tipo={tipoMensagem}
      />
 
      {sincronizando && (
        <div
          className={styles.syncStatus}
          role="status"
          aria-live="polite"
        >
          <span
            className={styles.syncSpinner}
            aria-hidden="true"
          />

          <span>
            Atualizando lista de funcionários...
          </span>
        </div>
      )}  
      {erroSincronizacao && (
        <div>
          <Alert
            mensagem={erroSincronizacao}
            tipo="erro"
          />

          <button
            type="button"
            className={styles.syncRetry}
            onClick={() => carregarFuncionarios(true)}
            disabled={sincronizando || processando}
          >
            <span aria-hidden="true">↻</span>
            Tentar novamente
          </button>
        </div>
      )}

      <header className={styles.header}>
        
        <div className={styles.headerTop}>
          <h2>Funcionários Cadastrados</h2>
          {status === 'sucesso' && (
            <button
              type="button"
              className={styles.refreshButton}
              onClick={() => carregarFuncionarios(true)}
              disabled={sincronizando || processando}
              aria-busy={sincronizando}
            >
              {sincronizando ? (
                <>
                  <span
                    className={styles.buttonSpinner}
                    aria-hidden="true"
                  />
                  Atualizando...
                </>
              ) : (
                "Atualizar funcionários"
              )}
            </button>
          )}
        </div>

        <div className={styles.searchContainer}>
          <input 
            type="text"
            value={pesquisa}
            className={styles.search}
            placeholder="Pesquisar funcionário..."
            onChange={(e) => setPesquisa(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                setPesquisa('')
              }
            }}
          />

          {pesquisa.length > 0 && (
            <button
              type="button"
              className={styles.clearSearchButton}
              onClick={() => setPesquisa("")}
            >
              Limpar pesquisa
            </button>
          )}
        </div>

        {status === 'sucesso' && (
          <p aria-live="polite" className={styles.resultsCount}>
            Exibindo {funcionariosFiltrados.length} de {itens.length} funcionários
          </p>
        )}
      </header>

      {status === 'carregando' ? (
        <Loading mensagem="Carregando funcionários..."/>

      ) : status === 'erro' ? (
        <div>
          <Alert
            mensagem={erro || 'Não foi possível carregar os funcionários.'}
            tipo="erro"
          />

          <button
            type="button"
            className={styles.retryButton}
            onClick={carregarFuncionarios}
          >
            Tentar novamente
          </button>
        </div>
      ) : (
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>E-mail</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {funcionariosFiltrados.map((item) => (
                <Fragment key={item.id}>
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.nome}</td>
                    <td>{item.email}</td>
                    <td>
                      <button 
                        type='button'
                        className={styles.expandButton}
                        onClick={() => alternarDetalhes(item.id)}
                        aria-expanded={funcionarioAberto === item.id}
                        aria-label={`Mostrar detalhes de ${item.nome}`}
                        disabled={processando}
                      >
                        {funcionarioAberto === item.id ? "▼" : "▶"}
                      </button>
                    </td>
                  </tr>

                  {funcionarioAberto === item.id && (
                    <tr className={styles.detailsRow}>
                      <td colSpan={4}>
                        <div className={styles.details}>
                          {[
                            { campo: "nome", titulo: "Nome", tipo: "text" },
                            { campo: "email", titulo: "Email", tipo: "email" },
                            { campo: "telefone", titulo: "Telefone", tipo: "tel" },
                            { campo: "cpf", titulo: "CPF", tipo: "text" }
                          ].map(({ campo, titulo, tipo }) => (
                            <div key={campo}>
                              <label htmlFor={`editar-${item.id}-${campo}`}>
                                {titulo}

                                {funcionarioEditando === item.id &&
                                  campoFoiAlterado(campo) && (
                                    <span className={styles.modifiedLabel}>
                                      (Modificado)
                                    </span>
                                  )}
                              </label>

                              {funcionarioEditando === item.id ? (
                                <input
                                  id={`editar-${item.id}-${campo}`} 
                                  type={tipo}
                                  value={dadosEdicao[campo]}
                                  disabled={processando}
                                  data-modificado={campoFoiAlterado(campo)}
                                  aria-label={`${titulo}${campoFoiAlterado(campo) ? " - modificado" : ""}`}
                                  onChange={(e) => {
                                    let valor = e.target.value

                                    if (campo === "telefone") {
                                      valor = formatarTelefone(valor)
                                    }

                                    if (campo === "cpf") {
                                      valor = formatarCpf(valor)
                                    }

                                    setDadosEdicao((atual) => ({
                                      ...atual,
                                      [campo]: valor
                                    }))
                                  }}
                                />
                              ) : (
                                <p>
                                  {
                                    campo === "telefone"
                                      ? formatarTelefone(item[campo])
                                      : campo === "cpf"
                                        ? formatarCpf(item[campo])
                                        : item[campo]
                                  }
                                </p>
                              )}
                            </div>
                          ))}

                          {funcionarioEditando !== item.id && (
                            <WorkerAccess
                              key={`${item.id}-${item.ativo}-${item.possui_acesso}`}
                              funcionario={item}
                              onUpdate={(atualizado) => setItens((anteriores) => anteriores.map((f) => f.id === atualizado.id ? atualizado : f))}
                            />
                          )}

                          <div className={styles.detailsActions}>
                            {funcionarioEditando === item.id ? (
                              <>                                                     
                                {temAlteracoes && !processando && (
                                  <span
                                    className={styles.unsavedChanges}
                                    role="status"
                                    aria-live="polite"
                                  >
                                    ⚠ Alterações não salvas
                                  </span>
                                )}

                                <button
                                  type="button"
                                  className={styles.restoreButton}
                                  onClick={restaurarEdicao}
                                  disabled={processando || !temAlteracoes}
                                >
                                  <span aria-hidden="true">↶</span>
                                  Restaurar
                                </button>
                        
                                <button
                                  type="button"
                                  className={styles.cancelButton}
                                  onClick={cancelarEdicao}
                                  disabled={processando}
                                >
                                  Cancelar
                                </button>

                                <button
                                  type="button"
                                  className={styles.saveButton}
                                  onClick={() => salvarEdicao(item.id)}
                                  disabled={processando || !temAlteracoes}
                                  aria-busy={Boolean(salvando)}
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
                                    "Salvar alterações"
                                  )}
                                </button>
                              </>
                            ) : funcionarioExcluindo === item.id ? (
                              <div className={styles.deleteConfirmation}>
                                <p>
                                  Tem certeza de que deseja excluir este funcionário?
                                  Essa ação não poderá ser desfeita.
                                </p>

                                <div className={styles.confirmationActions}>
                                  <button
                                    type="button"
                                    className={styles.cancelButton}
                                    onClick={() => setFuncionarioExcluindo(null)}
                                    disabled={processando}
                                  >
                                    Cancelar
                                  </button>
                 
                                  <button
                                    type="button"
                                    className={styles.deleteButton}
                                    onClick={() => excluirFuncionario(item.id)}
                                    disabled={processando}
                                    aria-busy={excluindo}
                                  >
                                    {excluindo ? (
                                      <>
                                        <span
                                          className={styles.buttonSpinner}
                                          aria-hidden="true"
                                        />
                                        Excluindo...
                                      </>
                                    ) : (
                                      "Confirmar exclusão"
                                    )}
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <>
                                <button
                                  type="button"
                                  className={styles.deleteButton}
                                  onClick={() => {
                                    setFuncionarioExcluindo(item.id)
                                    setMensagemEdicao("")
                                    setTipoMensagem("")
                                  }}
                                  disabled={processando}
                                >
                                  Excluir funcionário
                                </button>

                                <button
                                  type="button"
                                  onClick={() => iniciarEdicao(item)}
                                  disabled={processando}
                                >
                                  Editar funcionário
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
                ))}
                {funcionariosFiltrados.length === 0 && (
                  <tr>
                    <td colSpan={5}>  
                      {itens.length === 0
                        ? 'Nenhum funcionário cadastrado.'
                        : 'Nenhum funcionário corresponde à pesquisa.'}
                    </td>
                  </tr>
                )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}