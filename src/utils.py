import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

def serialize_update(weights, intercept, n_samples):
    """
    weights: numpy array (coef_)
    intercept: numpy array or float
    n_samples: int
    returns JSON string
    """
    payload = {
        'weights': np.array(weights).tolist(),   # shape (1, n_features)
        'intercept': np.array(intercept).tolist(),
        'n_samples': int(n_samples)
    }
    return json.dumps(payload, cls=NumpyEncoder)

def deserialize_update(s):
    payload = json.loads(s)
    import numpy as np
    w = np.array(payload['weights'])
    b = np.array(payload['intercept'])
    n = int(payload['n_samples'])
    return w, b, n
