from typing import List

from langchain.schema import Document
from langchain_redis import RedisVectorStore, RedisConfig

# from qna.llm import get_embeddings   # HAPUS
# from qna.llm import get_embeddings
from qna.embeddings import get_embeddings

from qna.constants import CACHE_TYPE, REDIS_INDEX_NAME, REDIS_URL


def get_cache():
    # construct cache implementation based on env var
    if CACHE_TYPE == "semantic":
        from langchain_redis import RedisSemanticCache
        print("Using semantic cache")
        # TODO change to using huggingface embeddings
        # so that caching is cheaper and faster.
        return RedisSemanticCache(
            redis_url='redis://10.100.34.246:12345',
            embeddings=get_embeddings(),
            distance_threshold=0.01
        )
    return None


def get_talent_vectorstore() -> RedisVectorStore:
    embeddings = get_embeddings()
    # config = RedisConfig.from_yaml("qna/arxiv.yaml", redis_url=REDIS_URL)


    vectorstore = RedisVectorStore.from_existing_index(
        embedding=embeddings,
        index_name="talent-pool",   # <--- ganti di sini
        redis_url='redis://10.100.34.246:12345',
        embedding_field="content_vector",
        content_field="content",
        metadata_field="metadata",
        key_prefix="doc:talent-pool:",
    )

    return vectorstore
    print("Connected to existing Redis index 'talent-pool' successfully.", vectorstore)
    return vectorstore


