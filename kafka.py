from confluent_kafka import Producer
import json

# Kafka producer configuration
kafka_config = {"bootstrap.servers": "localhost:9092"}

# Create a Kafka producer instance
producer = Producer(kafka_config)


# Define a function to send a message to the Kafka topic
def send_to_kafka(topic, message):
    message_json = json.dumps(message)
    producer.produce(topic, key="customer", value=message_json.encode("utf-8"))


# Close the producer when done
producer.flush()
