import logging
import pika
import json
from threading import Lock

from django.conf import settings

logging.getLogger("pika").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

EXCHANGE = 'topic'
EXCHANGE_TYPE = 'topic'


class QueueInteractor:
    """
    Base Class for interacting with queues, drawn from
        https://pika.readthedocs.io/en/0.10.0/examples/asynchronous_consumer_example.html
        https://pika.readthedocs.io/en/0.10.0/examples/asynchronous_publisher_example.html
    """
    def __init__(self, callback, route):
        self._on_exit = False
        self._connection = None
        self._channel = None
        self._callback = callback
        self._route = route

    def connect(self):
        parameters = pika.URLParameters(settings.AMPQ_CONNECTSTRING)
        parameters.heartbeat = 0
        return pika.SelectConnection(parameters,
                                     on_close_callback=self.on_connection_closed,
                                     on_open_callback=self.on_connection_open,
                                     on_open_error_callback=self.on_connection_error,
                                     stop_ioloop_on_close=False)

    def on_connection_closed(self, connection, code, text):
        log.warn("connection closed: {} - {}".format(code, text))
        self._channel = None
        if self._on_exit:
            self._connection.ioloop.stop()
        else:
            self._connection = connection
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_error(self, connection, msg):
        log.warn("connection error: {}".format(msg))
        self.on_connection_closed(connection, '-1', msg)

    def reconnect(self):
        self._connection.ioloop.stop()
        self._connection = self.connect()
        self._connection.ioloop.start()

    def on_connection_open(self, _):
        self.open_channel()

    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.exchange_declare(self.on_exchange_ok,
                                       exchange=EXCHANGE,
                                       type=EXCHANGE_TYPE,
                                       durable=True,
                                       auto_delete=False)

    def on_channel_closed(self, _, code, text):
        log.warn("channel closed: {} - {}".format(code, text))
        self._connection.close()

    def on_exchange_ok(self, _):
        pass

    def close_channel(self):
        if self._channel is not None:
            self._channel.close()

    def close_connection(self):
        if self._connection is not None:
            self._connection.close()

    def stop(self):
        pass


class QueueConsumer(QueueInteractor):
    """
    Base Class for consuming from queues, drawn from
        https://pika.readthedocs.io/en/0.10.0/examples/asynchronous_consumer_example.html
    """
    def __init__(self, callback, route):
        super().__init__(callback, route)
        self._consumer_tag = None

    def on_exchange_ok(self, _):
        self._channel.queue_declare(self.on_queue_ok,
                                    queue=self._route,
                                    durable=True,
                                    exclusive=False,
                                    auto_delete=False)

    def on_queue_ok(self, _):
        self._channel.queue_bind(self.on_bind_ok,
                                 queue=self._route,
                                 exchange=EXCHANGE,
                                 routing_key=self._route)

    def on_bind_ok(self, _):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._channel.basic_qos(prefetch_count=1)
        self._consumer_tag = self._channel.basic_consume(self._callback,
                                                         queue=self._route)

    def on_consumer_cancelled(self, _):
        if self._channel:
            self._channel.close()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, _):
        self._channel.close()

    def start(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        self._on_exit = True
        self.stop_consuming()
        self._connection.ioloop.start()


class QueuePublisher(QueueInteractor):
    def __init__(self, callback, route):
        super().__init__(callback, route)
        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = None

    def on_exchange_ok(self, _):
        self._connection.ioloop.stop()

    def send_messages(self, messages):
        if self._channel is None or not self._channel.is_open:
            return

        for message in messages:
            self._channel.basic_publish(exchange=EXCHANGE,
                                        routing_key=self._route,
                                        body=json.dumps(message, ensure_ascii=False).encode('utf8'),
                                        properties=pika.BasicProperties(
                                            content_type='application/json',
                                            delivery_mode=2
                                        ))
        self._message_number += len(messages)
        self._deliveries.append(self._message_number)

        if self._callback:
            self._callback()

    def start_sending(self, messages):
        self._connection = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        try:
            self._connection = self.connect()
            self._connection.ioloop.start()
            self.send_messages(messages)
        except Exception as e:
            self.stop()
            if (self._connection is not None and
                    not self._connection.is_closed):
                # Finish closing
                self._connection.ioloop.start()

    def stop(self):
        self._on_exit = True
        self.close_channel()
        self.close_connection()


class Scheduler:
    _route_out = ''

    def schedule_messages(self, override_route, messages):
        old_route = self._route_out
        self._route_out = override_route
        self.queue_result(messages=messages)
        self._route_out = old_route

    def queue_result(self, messages=None):
        qp = QueuePublisher(None, self._route_out)
        messages = self.get_messages() if messages is None else messages
        qp.start_sending(messages)
        qp.stop()

    def schedule(self):
        pass

    def get_messages(self):
        pass


class Listener:
    _route = ''
    _with_ack = True

    def listen_for(self):
        qs = QueueConsumer(self.digest_message_callback, self._route)
        qs.start()

    def digest_message_callback(self, channel, method, properties, body):
        with Lock():
            log.info("- received message {} for _route {} ".format(body, self._route))
            log.info("      - properties {}".format(properties))

            self.on_message(body)

            if self._with_ack:
                channel.basic_ack(delivery_tag = method.delivery_tag)

    def on_message(self, messagebody):
        pass


class Worker(Scheduler, Listener):
    _messages = []

    def get_messages(self):
        return self._messages

    def on_message(self, messagebody):
        self._messages = self.do_work_with_results(messagebody)
        self.queue_result()

    def do_work_with_results(self, messagebody):
        pass
