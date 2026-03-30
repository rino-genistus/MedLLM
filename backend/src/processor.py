import re
import string
import string
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import time
import json
from json_repair import repair_json
import unicodedata

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=60000,
    chunk_overlap=2000,
    separators=["\n### ", "\n## ", "\n# ", "\n\n", ". ", " "],
)

def get_useable_chunks(path):
    with open(path, "r") as f:
        text = f.read()
        print(len(text))
        punct_to_remove = string.punctuation
        #text = text.translate(str.maketrans('','',punct_to_remove))
        chunks_to_feed = re.findall(r'(Chapter\s+\d+[\s\S]*?)(?=Chapter\s+\d+|$)', text, re.IGNORECASE)
        if len(chunks_to_feed) == 0:
            chunks_to_feed = re.findall(r'(PAGE:\s+\d+[\s\S]*?)(?=PAGE:\s+\d+|$)', text, re.IGNORECASE)
        final_chunks = []
        for chunk in chunks_to_feed:
            if len(chunk) > 40000:
                sub_sections = text_splitter.split_text(chunk)
                final_chunks.extend(sub_sections)
            else:
                final_chunks.append(chunk)
    return final_chunks

def semantic_chunker(chunk_list):
    text_splitter = SemanticChunker(OpenAIEmbeddings())
    docs = []
    for chunk in chunk_list:
        docs.append(text_splitter.split_text(chunk))
    """for idx, chunk in enumerate(docs):
        if idx>20 and idx<30:
            print(f"INDEX: {idx}, CHUNK: {chunk} \n")"""
    return docs

def get_chunk_json(chunk_list, textbook_name):
    llm = ChatOpenAI(model='gpt-4o-mini', max_tokens=16000)
    template = ChatPromptTemplate.from_template(
        """You are a document processing expert. Split this document into as many chunks as required for maximum understanding and best semantic grouping. 
        For any areas of the document that have a figures, or tables or meaninful images, create a small description and tag it along with the chunk that it belongs too. If there are no tables or images, then just add an empty string.
        Follow these guidelines:
        
        1. Each chunk should contain complete ideas or concepts
        2. More complex sections should be in smaller chunks
        3. Preserve headers with their associated content
        4. Keep related information together
        5. Maintain the original order of the document
        6. Add a contexual header to the starting of each chunk so that it is easier to search through later when working with the RAG. Make sure the header is not just restating the title of the section but rather actually providing some insight on the topic and also includes the parent topic
        
        DOCUMENT:
        {doc}
        
        Return the output as a list of JSON objects with the following structure:
        [
            {{
                "header": "The section title",
                "content": "The actual text chunk",
                "description": "Description of any figures/tables in this chunk",
                "keywords": ["term1", "term2"],
                "requires_previous_context": "true or false",
                "summary": "One sentence context",
            }}
        ]

        Return ONLY the JSON array. Do not include any introductory or concluding text.
        """
    )
    chunking_chain = template | llm
    max_retries = 10
    retry_delay = 5

    content_list = []
    for idx, chunk in enumerate(chunk_list):
        print(f"CHUNK: {idx}")
        clean_chunk = chunk.encode("utf-8", "ignore").decode("utf-8")
        cleaner_chunk = unicodedata.normalize('NFKC', clean_chunk)
        response = chunking_chain.invoke({"doc": cleaner_chunk})
        content = response.content
        print("DEBUG content repr:", repr(content))
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            print("Strict JSON failed, attempting repair...")
            repaired_content = repair_json(content)
            parsed = json.loads(repaired_content)
        print(f"CONTENT: \n {content}")
        content_list.extend(parsed)

        filename = f"/Users/rino/MedLLM/MedLLM/data/processed/chunks_json_{textbook_name}.json"
        with open(filename, "w") as f:
            json.dump(content_list, f, indent=4)
        time.sleep(5)
        """except Exception as e:
            #Need for exception here is because the max number of tokens per minute or TPM is exceeded and requires more time to reload
            if "rate_limit_exceeded" in str(e).lower():
                print(f"Rate limit hit. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                #retry_delay *= 2   Double the wait time for the next try
            else:
                raise e
        raise Exception("Max retries exceeded")"""
    return content_list