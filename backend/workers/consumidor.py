import json
import logging
import os
import time
import pika
from sqlalchemy.exc import IntegrityError
from app import app
from extensions import db
from models.notificacao import Notificacao

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
LOGGER = logging.getLogger('consumidor')
FILA = 'culturapass.ingressos.v1'


def processar(mensagem):
    chave = mensagem['chave']
    tipo = mensagem['tipo']
    payload = mensagem['payload']
    evento_nome = str(payload.get('eventoNome', 'Evento'))[:120]
    ingresso_id = int(payload['ingressoId'])
    cliente_id = int(payload['clienteId'])
    textos = {
        'ingresso.emitido': f'Ingresso #{ingresso_id} emitido para {evento_nome}.',
        'ingresso.cancelado': f'Ingresso #{ingresso_id} cancelado para {evento_nome}.',
        'ingresso.reativado': f'Ingresso #{ingresso_id} reativado para {evento_nome}.'
    }
    if tipo not in textos:
        raise ValueError('Tipo de evento não permitido.')
    with app.app_context():
        existente = db.session.scalar(db.select(Notificacao.id).where(Notificacao.chave_evento == chave))
        if existente is not None:
            return
        db.session.add(Notificacao(chave_evento=chave, cliente_id=cliente_id, mensagem=textos[tipo]))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if db.session.scalar(db.select(Notificacao.id).where(Notificacao.chave_evento == chave)) is None:
                raise


def main():
    while True:
        conexao = None
        try:
            parametros = pika.URLParameters(os.environ['RABBITMQ_URL'])
            parametros.socket_timeout = 4
            parametros.connection_attempts = 1
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            canal.queue_declare(queue=FILA, durable=True)
            canal.basic_qos(prefetch_count=1)

            def ao_receber(ch, metodo, propriedades, corpo):
                try:
                    mensagem = json.loads(corpo)
                    processar(mensagem)
                    ch.basic_ack(delivery_tag=metodo.delivery_tag)
                    LOGGER.info('Mensagem processada e confirmada: %s', mensagem['chave'])
                except Exception:
                    LOGGER.exception('Falha ao processar mensagem; será reenviada.')
                    ch.basic_nack(delivery_tag=metodo.delivery_tag, requeue=True)
                    time.sleep(1)

            canal.basic_consume(queue=FILA, on_message_callback=ao_receber, auto_ack=False)
            LOGGER.info('Consumidor aguardando mensagens de %s', FILA)
            canal.start_consuming()
        except Exception:
            LOGGER.exception('Conexão com RabbitMQ perdida. Tentando reconectar.')
            time.sleep(3)
        finally:
            if conexao is not None and conexao.is_open:
                conexao.close()


if __name__ == '__main__':
    main()
