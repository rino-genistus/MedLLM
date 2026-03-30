import os
from pinecone import Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

embedding = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)

def create_content_list(chunks_json):
    all_content_list = [str(json_object.get('content')) for json_object in chunks_json]
    return all_content_list

def create_db():
    index_name = "hybrid-index"
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=1024,
            metric="dotproduct",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            )
        )
    return pc.Index(index_name)

def upsert_to_pinecone(chunks_json, bm25, hybrid_index, textbook_name):
    vectors_list = []
    for idx, json_object in enumerate(chunks_json):
        raw_content = json_object.get('content')
        if not isinstance(raw_content, str) or len(raw_content.strip())==0 or not raw_content:
            print(f"SKIPPING CHUNK {idx}")
            continue
        content_to_use = raw_content.strip()
        try:
            dense_vector_embedding = embedding.embed_query(content_to_use)
        except Exception as e:
            print(f"OPENAI FAILED ON CHUNK {idx}: ", e)
        sparse_vector_embedding = bm25.encode_documents(content_to_use)
        clean_json_object={
            "header":str(json_object.get('header', 'Unknown Section')),
            "content":str(json_object.get('content', '')),
            "description":str(json_object.get('description', '')),
            "requires_previous_context":str(json_object.get('requires_previous_content', '')).lower() == 'true',
            "summary":str(json_object.get('summary', '')),
        }

        raw_keywords = json_object.get('keywords', [])
        if isinstance(raw_keywords, list):
            clean_json_object['keywords'] = [str(k) for k in raw_keywords if k]
        else:
            clean_json_object['keywords'] = [str(raw_keywords)]

        vectors_list.append({
            "id":f"chunk-{idx}-{textbook_name}",
            "values":dense_vector_embedding,
            "sparse_values":sparse_vector_embedding,
            "metadata":clean_json_object,
        })

        if len(vectors_list) == 100:
            hybrid_index.upsert(vectors=vectors_list, namespace="MedLibrary")
            vectors_list=[]
    if len(vectors_list)>0:
        hybrid_index.upsert(vectors=vectors_list, namespace="MedLibrary")


def pine(chunks_json):
    for idx, json_object in enumerate(chunks_json):
        vector_embedding = embedding.embed_query(json_object['content'])
        print(f"JSON OBJECT INDEX: {idx}\n")
        print(f"VECTOR EMBEDDING: {str(vector_embedding)[:50]}")


def ask_medllm(query, bm25, hybrid_index):
    dense_query_embedding = embedding.embed_query(query)
    sparse_query_embedding = bm25.encode_documents(query)
    norm_dense, norm_sparse = hybrid_score_normalizer(dense_query_embedding, sparse_query_embedding, alpha=0.75)
    query_response = hybrid_index.query(
        namespace = "MedLibrary",
        top_k = 1000,
        vector = norm_dense,
        sparse_vector = norm_sparse,
        include_values = False,
        include_metadata = True,
    )
    context_for_ai = "\n\n".join([result['metadata']['content'] for result in query_response['matches']])
    prompt = """
    You are a medical school study assistant. 
    1. Answer the question based only on the context provided to you. If the context is about a specific technical subject, you may provide a brief 1-sentence general definition before diving into the context-specific details.
    2. Include any specific examples (like chemicals, experiments, or real-world applications) mentioned in the text.
    3. If the context describes a process, include the energy requirements or chemical formulas provided.
    4. If the answer to the questions doesn't exist in the context provided to you and cannot be reasonably inferred, reply by saying "I dont know the answer to this question". 
    5. Prioritize the provided text over outside knowledge. If the text contradicts common knowledge, follow the text.
    6. Cite the specific 'Header' from the metadata for each fact you state, exactly as it is.

    Context:
    {Context}

    Question:
    {Question}

    Answer:
    """
    prompt_ai = ChatPromptTemplate.from_template(prompt)
    chain = prompt_ai | llm
    answer_from_ai = chain.invoke({"Context": context_for_ai, "Question": query})
    return answer_from_ai.content

def hybrid_score_normalizer(dense_embedding, sparse_embedding, alpha):
    if alpha > 1 or alpha < 0:
        raise Exception("Alpha value must be between 0 and 1")
    norm_sparse_embedding = {
        'indices':sparse_embedding['indices'],
        'values':[v * (1-alpha) for v in sparse_embedding['values']]
    }
    return [v * alpha for v in dense_embedding], norm_sparse_embedding