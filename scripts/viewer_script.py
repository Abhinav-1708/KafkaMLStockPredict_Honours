#!/usr/bin/env python3
import joblib
import numpy as np
import os

def view_model(path, client_name):
    if not os.path.exists(path):
        print(f"{client_name} model not found at {path}")
        return
    model = joblib.load(path)
    print(f"\n=== {client_name} Model Summary ===")
    print(f"Keys: {list(model.keys())}")
    print(f"Coefficient shape: {model['coef_'].shape}")
    print(f"Intercept shape: {model['intercept_'].shape}")
    print("\nCoefficients:")
    print(np.round(model['coef_'][0], 4))
    print("\nIntercept:")
    print(np.round(model['intercept_'], 4))

def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    client1_path = os.path.join(base_dir, 'client1_model.joblib')
    client2_path = os.path.join(base_dir, 'client2_model.joblib')

    view_model(client1_path, "Client 1")
    view_model(client2_path, "Client 2")

if __name__ == '__main__':
    main()
