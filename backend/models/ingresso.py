from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


class Ingresso(db.Model):
    __tablename__ = 'ingressos'
    __table_args__ = (CheckConstraint("status IN ('ATIVO', 'CANCELADO')", name='ck_ingresso_status'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evento_id: Mapped[int] = mapped_column(Integer, ForeignKey('eventos.id', ondelete='RESTRICT'), nullable=False, index=True)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey('cliente.id', ondelete='RESTRICT'), nullable=False, index=True)
    adquirido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='ATIVO')
    evento = relationship('Evento', back_populates='ingressos')
