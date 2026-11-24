from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


class Evento(db.Model):
    __tablename__ = 'eventos'
    __table_args__ = (CheckConstraint('capacidade_maxima > 0', name='ck_evento_capacidade'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    local: Mapped[str] = mapped_column(String(200), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    capacidade_maxima: Mapped[int] = mapped_column(Integer, nullable=False)
    ingressos = relationship('Ingresso', back_populates='evento', lazy='selectin')
