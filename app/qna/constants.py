import os

# Env Vars and constants
CACHE_TYPE = os.getenv("CACHE_TYPE", "semantic")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "gpt-4o-mini")
OPENAI_EMBEDDINGS_ENGINE = os.getenv("OPENAI_EMBEDDINGS_ENGINE", "text-embedding-3-small")

REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "talent-pool")
REDIS_URL = os.getenv("REDIS_URL", "redis://10.100.34.246:12345")
