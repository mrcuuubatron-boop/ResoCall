import pika
import json
import os
import argparse
from typing import Optional


class RabbitMQProducer:
    def __init__(self, host: str = 'localhost', queue: str = 'asr_tasks'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=queue, durable=True)

    def send_task(self, audio_path: str, model: str = 'base', denoise: bool = True):
        """Отправляет задачу на обработку аудио."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(audio_path)

        task = {
            'audio_path': audio_path,
            'model': model,
            'denoise': denoise
        }
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=json.dumps(task),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(f" [x] Отправлена задача: {audio_path}")

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Producer для RabbitMQ")
    parser.add_argument("audio", help="Путь к аудиофайлу")
    parser.add_argument("--model", default="base", help="Модель Whisper")
    parser.add_argument("--no-denoise", action="store_false", dest="denoise", help="Отключить шумоподавление")
    parser.add_argument("--host", default="localhost", help="Хост RabbitMQ")
    args = parser.parse_args()

    producer = RabbitMQProducer(host=args.host)
    producer.send_task(args.audio, args.model, args.denoise)
    producer.close()
