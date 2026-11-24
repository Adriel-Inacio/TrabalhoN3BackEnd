from datetime import datetime, timezone
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(16), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    id_cliente: Mapped[int | None] = mapped_column(Integer, ForeignKey('cliente.id'), unique=True)
    id_funcionario: Mapped[int | None] = mapped_column(Integer, ForeignKey('funcionario.id'), unique=True)
    tentativas_falhas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bloqueado_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
