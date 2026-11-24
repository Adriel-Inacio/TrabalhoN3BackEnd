from sqlalchemy.exc import IntegrityError

from repositories.funcionarioRepository import (
    listar_funcionarios,
    inserir_funcionarios,
    atualizar_funcionario,
    excluir_funcionario
)

class FuncionarioInvalidError(Exception):
    pass

class IntegrityFuncionarioError(Exception):
    pass

class FuncionarioNotFoundError(Exception):
    pass

class FuncionarioDeleteError(Exception):
    pass

class DupCpfError(Exception):
    pass

def validar_cpf(cpf):
    numeros = "".join(caractere for caractere in cpf if caractere.isdigit())

    if len(numeros) != 11:
        return False

    if numeros ==numeros[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(
            int(numeros[i]) * (tamanho + 1 - i)
            for i in range(tamanho)
        )

        digito = (soma * 10) % 11

        if digito == 10:
            digito = 0

        if digito != int(numeros[tamanho]):
            return False

    return True

def normalizar_cpf(cpf):
    return "".join(
        caractere for caractere in cpf
        if caractere.isdigit()
    )

def validar_dados_funcionario(nome, email, telefone, cpf):
    campos = {
        "Nome": nome,
        "E-mail": email,
        "Telefone": telefone,
        "CPF": cpf
    }

    for campos, valor in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise FuncionarioInvalidError(
                f"O campo {campos} é obrigatório."
            )

    nome = nome.strip()
    email = email.strip()
    telefone = telefone.strip()
    cpf = cpf.strip()

    if len(nome) > 80:
        raise FuncionarioInvalidError(
            "O nome dever possuir no máximo 80 caracteres."
        )

    if len(email) > 80:
        raise FuncionarioInvalidError(
            "O e-mail deve possuir no máximo 80 caracteres"
        )

    if len(telefone) > 14:
        raise FuncionarioInvalidError(
            "O Telefone deve possuir no máximo 14 caracteres"
        )

    if len(cpf) > 14:
        raise FuncionarioInvalidError(
            "O CPF deve possuir no máximo 14 caracteres"
        )

    if not validar_cpf(cpf):
        raise FuncionarioInvalidError(
            "O CPF informado é inválido."
        )

    telefone = "".join(
        caractere for caractere in telefone
        if caractere.isdigit()
    )

    if len(telefone) != 11:
        raise FuncionarioInvalidError(
            "O telefone deve possuir exatamente 11 dígitos, incluindo o DDD."
        )

    cpf = normalizar_cpf(cpf)

    return {
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "cpf": cpf
    }

def verificar_integridade_funcionario (erro):
    erro_original = erro.orig

    codigo = getattr(erro_original, "sqlstate", None)

    diagnostico = getattr(erro_original, "diag", None)

    restricao = getattr(
        diagnostico,
        "constraint_name",
        None
    )

    if (
        codigo == "23505"
        and restricao == "funcionario_cpf_key"
    ):
        raise DupCpfError(
            "Este CPF já foi cadastrado para outro funcionário."
        ) from erro
    raise IntegrityFuncionarioError(
        "Não foi possível concluir a opração devido a uma restrição do banco."
    ) from erro

def obter_funcionarios():
    funcionarios = listar_funcionarios()

    return funcionarios

def cadastrar_funcionarios(nome, email, telefone, cpf):
    dados = validar_dados_funcionario(
        nome, email, telefone, cpf
    )

    try:
        funcionario = inserir_funcionarios(**dados)

        return funcionario

    except IntegrityError as erro:
        verificar_integridade_funcionario(erro)

def atualizar_dados_funcionario(id, nome, email, telefone, cpf):
    dados = validar_dados_funcionario(
        nome, email, telefone, cpf
    )

    try:
        funcionario = atualizar_funcionario(
            id=id,
            **dados
        )

        if funcionario is None:
            raise FuncionarioNotFoundError(
                "Funcionário não encontrado."
            )

        return funcionario
    
    except IntegrityError as erro:
        verificar_integridade_funcionario(erro)

def remover_funcionario(id):

    try:
        excluido = excluir_funcionario(id)

        if not excluido:
            raise FuncionarioDeleteError(
                "Funcionário não encontrado."
            )

        return True

    except IntegrityError as erro:

        codigo = getattr(erro.orig, "sqlstate", None)

        if codigo == "23503":
            raise FuncionarioDeleteError(
                "Não é possível excluir este funcionário "
                "porque existem registros vinculados a ele."
            ) from erro

        raise FuncionarioDeleteError(
            "Não foi possível excluir o funcionário "
            "devido a uma restrição do banco."
        ) from erro