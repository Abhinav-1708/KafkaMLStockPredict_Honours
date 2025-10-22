#!/usr/bin/env bash
set -e
source venv/bin/activate

echo "Starting Kafka (if not running)..."
docker compose up -d

echo "Creating topics..."
./scripts/create_topics.sh

echo "Resetting offsets..."
docker exec kafka kafka-consumer-groups.sh --bootstrap-server localhost:9092 --all-groups --reset-offsets --to-earliest --execute || true

echo "Running producer..."
python src/producer.py

echo "Running clients..."
python src/client_worker.py --client-id 1 &
PID1=$!
python src/client_worker.py --client-id 2 &
PID2=$!

wait $PID1
wait $PID2

echo "Running aggregator..."
python src/aggregator.py

echo "✅ Federated averaging complete. Check global_model.joblib"
