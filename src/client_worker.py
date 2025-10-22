#!/usr/bin/env python3
import os
import json
import argparse
import pandas as pd
import numpy as np
import time
from kafka import KafkaConsumer, KafkaProducer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from config import BOOTSTRAP_SERVERS, TOPIC_CLIENT1, TOPIC_CLIENT2, TOPIC_MODEL_UPDATES, RANDOM_SEED, NO_MESSAGE_WAIT_SECONDS
from utils import serialize_update

def consume_topic_until_idle(topic, idle_seconds=3):
    """
    Consume messages from topic until no new messages arrive for `idle_seconds`.
    Returns list of message dicts.
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        consumer_timeout_ms=1000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    records = []
    last_msg_time = time.time()
    try:
        while True:
            polled = consumer.poll(timeout_ms=1000, max_records=500)
            got_any = False
            for tp, msgs in polled.items():
                for msg in msgs:
                    records.append(msg.value)
                    got_any = True
                    last_msg_time = time.time()
            if not got_any:
                # If no messages in this poll, check idle period
                if time.time() - last_msg_time >= idle_seconds:
                    break
                # else continue polling until idle_seconds passes
    finally:
        consumer.close()
    return records

def prepare_features_labels(df):
    # expected columns from user (diagnosis + feature columns)
    if 'diagnosis' not in df.columns:
        raise ValueError("diagnosis column missing")
    X = df.drop(columns=['diagnosis'])
    y = df['diagnosis'].astype(int)
    # convert all to numeric
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0.0)
    return X, y

def train_and_send(client_id, topic):
    print(f"[Client {client_id}] consuming from topic {topic} ...")
    records = consume_topic_until_idle(topic, idle_seconds=NO_MESSAGE_WAIT_SECONDS)
    if not records:
        print(f"[Client {client_id}] No records consumed. Exiting.")
        return
    df = pd.DataFrame(records)
    X, y = prepare_features_labels(df)

    # Train logistic regression
    model = LogisticRegression(max_iter=5000, solver='lbfgs', random_state=RANDOM_SEED)
    model.fit(X, y)

    weights = model.coef_   # shape (1, n_features)
    intercept = model.intercept_
    n_samples = X.shape[0]

    payload = serialize_update(weights, intercept, n_samples)

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: v.encode('utf-8'),
        api_version=(2, 8, 1)
    )
    producer.send(TOPIC_MODEL_UPDATES, payload)
    producer.flush()
    print(f"[Client {client_id}] Sent model update (n_samples={n_samples}) to {TOPIC_MODEL_UPDATES}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--client-id', type=int, required=True, choices=[1,2])
    args = parser.parse_args()
    topic = TOPIC_CLIENT1 if args.client_id == 1 else TOPIC_CLIENT2
    train_and_send(args.client_id, topic)
