from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from qna.constants import OPENAI_EMBEDDINGS_ENGINE

def get_embeddings() -> Embeddings:
    return OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_ENGINE)
