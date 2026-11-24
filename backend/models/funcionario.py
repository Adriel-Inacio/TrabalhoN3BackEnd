from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from extensions import db

class Funcionario(db.Model):
    __tablename__ = "funcionario"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    telefone: Mapped[str] = mapped_column(
        String(11),
        nullable=False
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<Funcionario {self.nome}>"