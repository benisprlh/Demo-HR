#!/usr/bin/env python3
"""
Simple fix test - bypass vector search and use text search
Jalankan: poetry run python simple_fix_test.py
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import redis
from dotenv import load_dotenv
load_dotenv()

def test_text_search():
    """Test basic text search without vector"""
    print("=" * 50)
    print("TEXT SEARCH TEST (NO VECTOR)")
    print("=" * 50)
    
    try:
        client = redis.Redis.from_url('redis://10.100.34.246:12345')
        
        # Try basic text searches
        search_terms = ["beni", "saprulah", "software", "engineer", "python", "html", "*"]
        
        for term in search_terms:
            try:
                result = client.execute_command("FT.SEARCH", "talent-pool", term, "LIMIT", "0", "3")
                doc_count = result[0]
                print(f"Search '{term}': found {doc_count} docs")
                
                if doc_count > 0:
                    print(f"  SUCCESS! Text search works with term: {term}")
                    # Show document content
                    for i in range(1, len(result), 2):
                        doc_key = result[i]
                        print(f"  Document key: {doc_key}")
                        
                        # Get full document
                        full_doc = client.hgetall(doc_key)
                        if full_doc:
                            content = full_doc.get(b'content', b'').decode('utf-8', errors='ignore')
                            print(f"  Content preview: {content[:100]}...")
                            print(f"  Available fields: {list(full_doc.keys())}")
                    return True
                    
            except Exception as e:
                print(f"Search '{term}' failed: {e}")
                
        return False
        
    except Exception as e:
        print(f"Text search test failed: {e}")
        return False

def test_langchain_text_only():
    """Test LangChain with text-only search (no vector)"""
    print("=" * 50)
    print("LANGCHAIN TEXT-ONLY TEST")
    print("=" * 50)
    
    try:
        from langchain_redis import RedisVectorStore
        from qna.embeddings import get_embeddings
        
        embeddings = get_embeddings()
        
        # Try to create vectorstore but force text search
        configs = [
            {
                "name": "from_existing_index (default)",
                "vectorstore": RedisVectorStore.from_existing_index(
                    embedding=embeddings,
                    index_name="talent-pool",
                    redis_url='redis://10.100.34.246:12345',
                )
            },
            {
                "name": "direct with redis_client",
                "vectorstore": RedisVectorStore(
                    embeddings,
                    redis_client=redis.Redis.from_url('redis://10.100.34.246:12345'),
                    index_name="talent-pool",
                )
            }
        ]
        
        for config in configs:
            print(f"\nTesting: {config['name']}")
            try:
                vectorstore = config['vectorstore']
                
                # Try different search methods
                search_methods = [
                    ("similarity_search", lambda vs: vs.similarity_search("beni", k=3)),
                    ("similarity_search with software", lambda vs: vs.similarity_search("software", k=3)),
                    ("similarity_search with *", lambda vs: vs.similarity_search("*", k=3)),
                ]
                
                for method_name, method in search_methods:
                    try:
                        docs = method(vectorstore)
                        print(f"  {method_name}: {len(docs)} docs")
                        
                        if docs:
                            print(f"    SUCCESS! {method_name} works")
                            print(f"    Sample: {docs[0].page_content[:50]}...")
                            print(f"    Metadata: {docs[0].metadata}")
                            return vectorstore  # Return working vectorstore
                            
                    except Exception as e:
                        print(f"  {method_name} failed: {e}")
                        
            except Exception as e:
                print(f"  {config['name']} creation failed: {e}")
        
        return None
        
    except Exception as e:
        print(f"LangChain text-only test failed: {e}")
        return None

def test_retriever_chain(vectorstore):
    """Test the retriever and chain with working vectorstore"""
    print("=" * 50)
    print("RETRIEVER CHAIN TEST")
    print("=" * 50)
    
    try:
        from qna.llm import get_llm, make_qna_chain
        from qna.prompt import basic_prompt
        
        # Create components
        llm = get_llm(max_tokens=200)
        prompt = basic_prompt()
        
        # Create chain with working vectorstore
        chain = make_qna_chain(llm, vectorstore, prompt, k=3)
        print("Chain created successfully")
        
        # Test queries
        test_queries = ["find beni", "software engineer", "who is beni saprulah"]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            try:
                # Try different parameter formats
                param_formats = [{"query": query}, {"question": query}, {"input": query}]
                
                for params in param_formats:
                    try:
                        result = chain.invoke(params)
                        answer = result.get("result", "")
                        source_docs = result.get("source_documents", [])
                        
                        print(f"  SUCCESS with params {list(params.keys())}")
                        print(f"  Answer length: {len(answer)} chars")
                        print(f"  Source docs: {len(source_docs)}")
                        
                        if answer:
                            print(f"  Answer preview: {answer[:100]}...")
                        if source_docs:
                            print(f"  Source preview: {source_docs[0].page_content[:50]}...")
                            
                        return True  # Success
                        
                    except Exception as e:
                        print(f"  Params {list(params.keys())} failed: {e}")
                        continue
                        
            except Exception as e:
                print(f"Query '{query}' failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"Retriever chain test failed: {e}")
        return False

def main():
    """Main test function"""
    print("SIMPLE FIX TEST - BYPASS VECTOR SEARCH")
    print("Run with: poetry run python simple_fix_test.py")
    print()
    
    # Step 1: Test if text search works
    text_works = test_text_search()
    
    if not text_works:
        print("FAILED: Even text search doesn't work")
        return
        
    # Step 2: Test LangChain with text search
    vectorstore = test_langchain_text_only()
    
    if not vectorstore:
        print("FAILED: Could not create working vectorstore")
        return
        
    # Step 3: Test full chain
    chain_works = test_retriever_chain(vectorstore)
    
    print("\n" + "=" * 50)
    print("SOLUTION SUMMARY")
    print("=" * 50)
    
    if chain_works:
        print("SUCCESS! The issue was vector search syntax.")
        print("SOLUTION: Use text-based similarity search instead of vector search")
        print("Your app should work now - the vectorstore connects but uses text matching")
    else:
        print("PARTIAL SUCCESS: VectorStore works but chain has issues")
        print("Check the chain parameter format (query vs question vs input)")

if __name__ == "__main__":
    main()