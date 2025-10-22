#!/usr/bin/env python3
import pandas as pd
import json
import time
from kafka import KafkaProducer
import os
from sklearn.model_selection import train_test_split
from config import BOOTSTRAP_SERVERS, TOPIC_CLIENT1, TOPIC_CLIENT2

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'breast-cancer.csv')

def load_and_prepare(csv_path):
    df = pd.read_csv(csv_path)
    
    # Drop id column if present
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    # Encode diagnosis: M=1, B=0
    if 'diagnosis' not in df.columns:
        raise ValueError("Expected column 'diagnosis' in dataset.")
    df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})
    
    # Drop rows with missing values
    df = df.dropna().reset_index(drop=True)

    return df

def main():
    df = load_and_prepare(CSV_PATH)

    # Split dataset 50/50, stratified by label
    client1_df, client2_df = train_test_split(
        df, test_size=0.5, random_state=42, stratify=df['diagnosis']
    )

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(2, 8, 1)
    )

    print(f"Streaming {len(client1_df)} records to {TOPIC_CLIENT1}")
    for _, row in client1_df.iterrows():
        producer.send(TOPIC_CLIENT1, row.to_dict())
    producer.flush()
    print(f"Done streaming to {TOPIC_CLIENT1}")

    print(f"Streaming {len(client2_df)} records to {TOPIC_CLIENT2}")
    for _, row in client2_df.iterrows():
        producer.send(TOPIC_CLIENT2, row.to_dict())
    producer.flush()
    print(f"Done streaming to {TOPIC_CLIENT2}")

if __name__ == '__main__':
    main()
