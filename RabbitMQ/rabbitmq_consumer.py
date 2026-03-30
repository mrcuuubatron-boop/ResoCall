import pika
import json
import os
import argparse
from ASR import CallAnalyzer
from rabbitmq_producer import RabbitMQProducer  # для отправки результата, если нужно


class RabbitMQConsumer:
    def __init__(self, host: str = 'localhost', input_queue: str = 'asr_tasks',
                 output_queue: Optional[str] = None):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.channel.queue_declare(queue=input_queue, durable=True)
        if output_queue:
            self.channel.queue_declare(queue=output_queue, durable=True)

    def callback(self, ch, method, properties, body):
        task = json.loads(body)
        audio_path = task['audio_path']
        model = task.get('model', 'base')
        denoise = task.get('denoise', True)

        print(f" [x] Получена задача: {audio_path}")

        # Обработка
        analyzer = CallAnalyzer(asr_model_name=model, denoise=denoise)
        try:
            result = analyzer.analyze(audio_path)
            # Сохраняем результат (например, в файл или отправляем обратно)
            if self.output_queue:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.output_queue,
                    body=json.dumps(result),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
            else:
                # Сохраняем локально
                out_path = f"results/{os.path.basename(audio_path)}.json"
                os.makedirs("results", exist_ok=True)
                with open(out_path, 'w') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f" [x] Результат сохранён в {out_path}")
        except Exception as e:
            print(f" [x] Ошибка при обработке {audio_path}: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.input_queue, on_message_callback=self.callback)
        print(' [*] Ожидание задач. Для выхода нажмите CTRL+C')
        self.channel.start_consuming()

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Consumer для RabbitMQ")
    parser.add_argument("--host", default="localhost", help="Хост RabbitMQ")
    parser.add_argument("--queue", default="asr_tasks", help="Имя очереди")
    parser.add_argument("--output-queue", help="Имя очереди для результатов (опционально)")
    args = parser.parse_args()

    consumer = RabbitMQConsumer(host=args.host, input_queue=args.queue, output_queue=args.output_queue)
    try:
        consumer.start()
    except KeyboardInterrupt:
        consumer.close()
