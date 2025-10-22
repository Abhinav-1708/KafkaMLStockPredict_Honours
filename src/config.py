BOOTSTRAP_SERVERS = 'localhost:9092'

TOPIC_CLIENT1 = 'client1-data'
TOPIC_CLIENT2 = 'client2-data'
TOPIC_MODEL_UPDATES = 'model-updates'
TOPIC_GLOBAL = 'global-model'

# model settings
MODEL_TYPE = 'logistic'  # sklearn LogisticRegression
RANDOM_SEED = 42

# consumption behavior
NO_MESSAGE_WAIT_SECONDS = 3  # stop polling after N seconds with no new messages
