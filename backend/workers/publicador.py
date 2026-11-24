import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
import pika
from app import app
from extensions import db
from models.outbox import Outbox

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
LOGGER = logging.getLogger('publicador')
FILA = 'culturapass.ingressos.v1'


def publicar_um():
    with app.app_context():
        evento = db.session.execute(db.select(Outbox).where(
            Outbox.estado == 'PENDENTE',
            db.or_(Outbox.proxima_tentativa.is_(None), Outbox.proxima_tentativa <= datetime.now(timezone.utc))
        ).order_by(Outbox.id).limit(1).with_for_update(skip_locked=True)).scalar_one_or_none()
        if evento is None:
            db.session.rollback()
            return False
        conexao = None
        try:
            parametros = pika.URLParameters(os.environ['RABBITMQ_URL'])
            parametros.socket_timeout = 3
            parametros.blocked_connection_timeout = 5
            parametros.connection_attempts = 1
            conexao = pika.BlockingConnection(parametros)
            canal = conexao.channel()
            canal.queue_declare(queue=FILA, durable=True)
            canal.confirm_delivery()
            mensagem = {'chave': evento.chave, 'tipo': evento.tipo, 'payload': evento.payload}
            confirmado = canal.basic_publish(
                exchange='', routing_key=FILA,
                body=json.dumps(mensagem, ensure_ascii=False).encode('utf-8'),
                properties=pika.BasicProperties(content_type='application/json', delivery_mode=2),
                mandatory=True
            )
            if confirmado is False:
                raise RuntimeError('Publicação sem confirmação do broker.')
            evento.estado = 'ENVIADO'
            evento.publicado_em = datetime.now(timezone.utc)
            evento.ultimo_erro = None
            db.session.commit()
            LOGGER.info('Publicado evento %s tipo=%s', evento.chave, evento.tipo)
        except Exception as erro:
            evento.tentativas += 1
            atraso = min(2 ** min(evento.tentativas, 7), 120)
            evento.proxima_tentativa = datetime.now(timezone.utc) + timedelta(seconds=atraso)
            evento.ultimo_erro = str(erro)[:500]
            db.session.commit()
            LOGGER.warning('Broker indisponível, reenvio de %s em %ss: %s', evento.chave, atraso, erro)
        finally:
            if conexao is not None and conexao.is_open:
                conexao.close()
        return True


def main():
    while True:
        try:
            ocupado = publicar_um()
            if not ocupado:
                time.sleep(1)
        except Exception:
            LOGGER.exception('Falha no processo de publicação; haverá nova tentativa.')
            time.sleep(3)


if __name__ == '__main__':
    main()
