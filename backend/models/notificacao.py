from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from extensions import db


class Notificacao(db.Model):
    __tablename__ = 'notificacoes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chave_evento: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('cliente.id', ondelete='RESTRICT'), nullable=False, index=True)
    mensagem: Mapped[str] = mapped_column(String(300), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
