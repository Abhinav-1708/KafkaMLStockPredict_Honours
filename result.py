import joblib
import numpy as np

model = joblib.load('global_model.joblib')

print("\n=== Global Model Summary ===")
print(f"Keys: {list(model.keys())}")
print(f"Coefficient shape: {model['coef_'].shape}")
print(f"Intercept shape: {model['intercept_'].shape}")

# Optional: print a few weights
print("\nCoefficients:")
print(np.round(model['coef_'][0], 4))

print("\nIntercept:")
print(np.round(model['intercept_'], 4))
