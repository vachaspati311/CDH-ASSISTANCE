import os

class EmbeddingConfig:
    MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    DIMENSIONS = 3072
    BATCH_SIZE = 100
