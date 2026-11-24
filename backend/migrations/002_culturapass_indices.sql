CREATE INDEX IF NOT EXISTS idx_ingressos_evento_status ON ingressos(evento_id, status);
CREATE INDEX IF NOT EXISTS idx_ingressos_cliente_evento_status ON ingressos(cliente_id, evento_id, status);
CREATE INDEX IF NOT EXISTS idx_outbox_estado_tentativa ON outbox_eventos(estado, proxima_tentativa, id);
CREATE INDEX IF NOT EXISTS idx_notificacoes_cliente_data ON notificacoes(cliente_id, criado_em DESC);
