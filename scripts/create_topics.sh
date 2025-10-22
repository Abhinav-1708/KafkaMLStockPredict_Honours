#!/usr/bin/env bash
# Run from project root after docker-compose up -d

KAFKA_CONTAINER=kafka

# topics
topics=("client1-data" "client2-data" "model-updates" "global-model")

for t in "${topics[@]}"; do
  docker exec $KAFKA_CONTAINER kafka-topics.sh --create --topic $t --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || \
  echo "Topic $t might already exist"
done

docker exec $KAFKA_CONTAINER kafka-topics.sh --list --bootstrap-server localhost:9092
