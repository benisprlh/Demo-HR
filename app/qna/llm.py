from typing import TYPE_CHECKING
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.llms.base import LLM
from langchain_redis import RedisVectorStore
from qna.constants import OPENAI_COMPLETIONS_ENGINE

def get_llm(max_tokens=1000) -> LLM:
    llm = ChatOpenAI(
        model_name=OPENAI_COMPLETIONS_ENGINE, 
        max_tokens=max_tokens,
        temperature=0.1  # Tambahkan untuk consistency
    )
    return llm

def make_qna_chain(llm: LLM, vector_db: RedisVectorStore, prompt=None, **kwargs):
    """Create QA chain with better configuration"""
    
    search_type = "similarity"
    if "search_type" in kwargs:
        search_type = kwargs.pop("search_type")
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs=kwargs, search_type=search_type),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
        verbose=True,
    )
    return chain