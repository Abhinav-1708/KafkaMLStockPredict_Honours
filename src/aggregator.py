#!/usr/bin/env python3
import time
import numpy as np
import joblib
import os
from kafka import KafkaConsumer, KafkaProducer
from utils import deserialize_update
from config import BOOTSTRAP_SERVERS, TOPIC_MODEL_UPDATES, TOPIC_GLOBAL

MODEL_OUT = os.path.join(os.path.dirname(__file__), '..', 'global_model.joblib')

def weighted_average(updates):
    total = sum(u[2] for u in updates)
    w_sum = None
    b_sum = None
    for w, b, n in updates:
        w = np.array(w, dtype=float)
        b = np.array(b, dtype=float)
        if w_sum is None:
            w_sum = w * n
            b_sum = b * n
        else:
            w_sum += w * n
            b_sum += b * n
    w_avg = w_sum / total
    b_avg = b_sum / total
    return w_avg, b_avg

def collect_updates(expected_clients=2, overall_timeout=30):
    consumer = KafkaConsumer(
        TOPIC_MODEL_UPDATES,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: m.decode('utf-8')
    )
    updates = []
    start = time.time()
    print("[Aggregator] Listening for model updates...")
    while True:
        # blocking poll for small interval
        msg_pack = consumer.poll(timeout_ms=2000, max_records=100)
        if msg_pack:
            for tp, messages in msg_pack.items():
                for msg in messages:
                    try:
                        w, b, n = deserialize_update(msg.value)
                        updates.append((w, b, n))
                        print("[Aggregator] Received update n_samples=", n)
                    except Exception as e:
                        print("Failed to parse update:", e)
        # break conditions
        if len(updates) >= expected_clients:
            print(f"[Aggregator] Collected expected {expected_clients} updates.")
            break
        if time.time() - start > overall_timeout:
            print(f"[Aggregator] Timeout ({overall_timeout}s) reached, collected {len(updates)} updates.")
            break
    consumer.close()
    return updates

def publish_global_model(coef, intercept):
    payload = {
        'coef_': coef.tolist(),
        'intercept_': intercept.tolist()
    }
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(TOPIC_GLOBAL, payload)
    producer.flush()
    print("[Aggregator] Published global model to", TOPIC_GLOBAL)

def main():
    updates = collect_updates(expected_clients=2, overall_timeout=30)
    if not updates:
        print("[Aggregator] No updates received; exiting.")
        return
    coef, intercept = weighted_average(updates)
    # store simple dict
    global_model = {'coef_': coef, 'intercept_': intercept}
    joblib.dump(global_model, MODEL_OUT)
    print("[Aggregator] Saved global model to", MODEL_OUT)

    # publish global model as JSON (use only if you implement rounds later)
    # NOTE: json import locally to avoid unused import earlier
    import json
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(2, 8, 1)
    )
    publish_payload = {'coef_': coef.tolist(), 'intercept_': intercept.tolist()}
    producer.send(TOPIC_GLOBAL, publish_payload)
    producer.flush()
    print("[Aggregator] Published global model to", TOPIC_GLOBAL)

if __name__ == '__main__':
    main()
