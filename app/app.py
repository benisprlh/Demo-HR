import os
import time
import json
import langchain
import streamlit as st
import redis

from collections import defaultdict
from urllib.error import URLError
from dotenv import load_dotenv

# ---- Load env & debug ----
load_dotenv()
if os.environ.get("QNA_DEBUG") == "true":
    langchain.debug = True

# ---- Local imports (project) ----
from langchain.globals import set_llm_cache
from qna.llm import make_qna_chain, get_llm
from qna.db import get_talent_vectorstore, get_cache
from qna.prompt import basic_prompt
from qna.constants import REDIS_URL  # if you need it elsewhere

# ---- Streamlit Page Config (optional) ----
st.set_page_config(page_title="Chatbot HR Talent Sourcing Assistant", layout="wide")

# =========================
# Cache Activation (GLOBAL)
# =========================
@st.cache_resource
def fetch_llm_cache():
    """Return semantic cache (or None) from qna.db.get_cache."""
    return get_cache()

# Activate semantic cache before creating any LLM or chain:
_cache = fetch_llm_cache()
if _cache:
    set_llm_cache(_cache)

# =========================
# Sidebar: (clean) Controls only
# =========================
with st.sidebar:
    st.write("## LLM Settings")
    st.slider("Number of Tokens", 100, 8000, 400, key="max_tokens")

    st.write("## Retrieval Settings")
    st.slider("Number of Context Documents", 2, 20, 5, key="num_context_docs")

    st.write("## App Settings")
    st.button("Clear Chat", key="clear_chat", on_click=lambda: st.session_state['messages'].clear())
    st.button("New Conversation", key="reset", on_click=lambda: reset_app())
    st.button("Clear Cache", key="clear_cache", on_click=lambda: clear_cache())

def clear_cache():
    if not st.session_state.get("llm"):
        st.warning("Could not find llm to clear cache of")
        return
    llm = st.session_state["llm"]
    llm_string = llm._get_llm_string()
    langchain.llm_cache.clear(llm_string=llm_string)
    st.success("✅ Cleared semantic cache for current LLM")

def reset_app():
    st.session_state['messages'].clear()
    st.session_state['context'] = []
    st.session_state['response'] = ""

# =========================
# Defaults / Session state
# =========================
prompt = basic_prompt()
defaults = {
    "response": "",
    "context": [],
    "chain": None,
    "llm": None,
    "messages": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# Main UI
# =========================
st.title("Chatbot HR Talent Sourcing Assistant")

# ---- Init LLM ----
if st.session_state["llm"] is None:
    tokens = st.session_state["max_tokens"]
    st.session_state["llm"] = get_llm(max_tokens=tokens)

# ---- Init Chain (VectorStore + RAG chain) ----
if st.session_state["chain"] is None:
    try:
        with st.spinner("Connecting to Redis vectorstore..."):
            vector_db = get_talent_vectorstore()
            st.session_state["chain"] = make_qna_chain(
                st.session_state["llm"],
                vector_db,
                prompt=prompt,
                k=st.session_state['num_context_docs'],
                search_type="similarity",
            )
        st.success("✅ Connected to Redis successfully!")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        # (COMMENTED) verbose traceback UI
        # st.info("💡 Check the debug info in sidebar")
        # import traceback
        # st.code(traceback.format_exc())
        st.stop()

# =========================
# Chat History Rendering
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# Chat Input & Handling
# =========================
if query := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        chain = st.session_state['chain']

        start_time = time.time()
        try:
            parameter_attempts = [
                {"query": query},
                {"question": query},
                {"input": query},
            ]
            result = None
            for i, params in enumerate(parameter_attempts, start=1):
                try:
                    # (COMMENTED) Attempt logs in UI
                    # st.info(f"Attempt {i}: Using parameters {list(params.keys())}")
                    result = chain.invoke(params)
                    break
                except Exception as e:
                    # st.warning(f"Attempt {i} failed: {e}")
                    continue

            if not result:
                st.error("All parameter attempts failed!")
                st.stop()

            elapsed = time.time() - start_time
            answer = result.get("result", "")
            source_docs = result.get("source_documents", [])

            st.markdown(answer if answer else "No answer generated")

            # Heuristic "cache-like" indicator
            cache_like = elapsed < 0.6  # adjust threshold based on your infra
            info_line = f"⏱️ Response time: {elapsed:.2f} detik | 📄 {len(source_docs)} docs"
            info_line += " (✅ cache-like)" if cache_like else " (⚡ fresh-like)"
            st.caption(info_line)

            # Persist to session
            st.session_state['context'] = source_docs
            st.session_state['response'] = answer
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # ---- Render context documents (kept; not debug) ----
            if source_docs:
                with st.expander("Context Documents"):
                    by_title = defaultdict(list)
                    for doc in source_docs:
                        title = doc.metadata.get('filename', doc.metadata.get('title', 'Untitled'))
                        by_title[title].append(doc)
                    for i, (title, doc_list) in enumerate(by_title.items(), 1):
                        st.write(f"{i}. **{title}**")
                        for ctx_idx, doc in enumerate(doc_list, 1):
                            st.write(f" - **Context {ctx_idx}**: {doc.page_content[:200]}...")
                            st.write(f" - **Metadata**: {doc.metadata}")
            # else:
            #     st.warning("No context documents to display")

        except Exception as e:
            st.error(f"❌ Chain execution failed: {e}")
            # (COMMENTED) verbose traceback UI
            # import traceback
            # st.code(traceback.format_exc())

# =========================
# (COMMENTED) Troubleshooting note in sidebar
# =========================
# st.sidebar.markdown("""
# ---
# **Troubleshooting:**
# - Ensure Redis is running
# - Verify API key is set
# - Check if index has data
# """)
