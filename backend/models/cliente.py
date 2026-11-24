from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from extensions import db

class Cliente(db.Model):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, nullable = False)
    nome: Mapped[String] = mapped_column(String(80), nullable = False)
    email: Mapped[String] = mapped_column(String(80), nullable = False)
    senha_hash: Mapped[String] = mapped_column(String(255), nullable = False)
    telefone: Mapped[String] = mapped_column(String(14), nullable = False)

    def __repr__(self):
            return f"<Cliente {self.nome}>"