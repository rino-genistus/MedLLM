import requests
from bs4 import BeautifulSoup
import os
import io
import pdfplumber
from pinecone import ServerlessSpec, Pinecone
import string
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re
import time
import json

pc = Pinecone(api_key="pcsk_7L8ZJC_MnLCjKrXF2PtKzgY23pKcguAAhxHKjh6esHa1tREhWTsd4CSYdjCPwfxbEabvL7")

books = {
    "Biology2e": "https://assets.openstax.org/oscms-prodcms/media/documents/Biology2e-WEB.pdf",
    "Chemistry2e": "https://assets.openstax.org/oscms-prodcms/media/documents/Chemistry2e-WEB.pdf",
    "Anatomy and Physiology 2e": "https://assets.openstax.org/oscms-prodcms/media/documents/Anatomy_and_Physiology_2e_-_WEB_c9nD9QL.pdf",
    "Physics": "https://assets.openstax.org/oscms-prodcms/media/documents/University_Physics_Volume_1_-_WEB.pdf",
    "Psychology2e": "https://assets.openstax.org/oscms-prodcms/media/documents/Psychology2e_WEB.pdf",
    "Sociology3e": "https://assets.openstax.org/oscms-prodcms/media/documents/IntroductiontoSociology3e-WEB.pdf",
    "Statistics": "https://assets.openstax.org/oscms-prodcms/media/documents/Introductory_Statistics_2e_-_WEB.pdf",
    "Calculus1": "https://assets.openstax.org/oscms-prodcms/media/documents/Calculus_Volume_1_-_WEB_l4sAIKd.pdf",
}

chosen_books = {
    "Chemistry2e": "https://assets.openstax.org/oscms-prodcms/media/documents/Chemistry2e-WEB.pdf",
}

os.makedirs("DIAGRAMS", exist_ok=True)
os.makedirs("TEXTBOOKS", exist_ok=True)


def create_text_and_images(books):
    for name, url in books.items():
        response = requests.get(url)
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            with open(f"TEXTBOOKS/{name}.txt", "w") as f:
                for page_num, page in enumerate(pdf.pages):
                    if page_num+1>22:
                        text = page.extract_text()
                        if text and text.strip():
                            f.write(f"PAGE: {page_num + 1}\n")
                            f.write(f"{text}\n")
                    """for i, image in enumerate(page.images):
                        x0 = max(0, image['x0'])
                        top = max(0, image['top'])
                        x1 = min(page.width, image['x1'])
                        bottom = min(page.height, image['bottom'])

                        if x1 > x0 and bottom>top:
                            bbox = (x0, top, x1, bottom)
                            cropped_page = page.within_bbox(bbox)
                            img = cropped_page.to_image(resolution=300)
                            img.save(f"DIAGRAMS/{name}/page_{page.page_number}_img_{i+1}.png")"""

#create_text_and_images(chosen_books)

with open("/Users/rino/MedLLM/MedLLM/TEXTBOOKS/Chemistry2e.txt", "r") as f:
    text = f.read()
    print(len(text))
    punct_to_remove = string.punctuation
    #text = text.translate(str.maketrans('','',punct_to_remove))
    chunk_list = re.findall(r'(Chapter\s+\d+[\s\S]*?)(?=Chapter\s+\d+|$)', text, re.IGNORECASE)


def get_chunks(chunk_list):
    text_splitter = SemanticChunker(OpenAIEmbeddings())
    docs = []
    for chunk in chunk_list:
        docs.append(text_splitter.split_text(chunk))
    """for idx, chunk in enumerate(docs):
        if idx>20 and idx<30:
            print(f"INDEX: {idx}, CHUNK: {chunk} \n")"""
    return docs

"""docs = get_chunks(chunk_list)
print(docs[0])
print(len(docs[0]))"""

llm = ChatOpenAI(model='gpt-4o')
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
            7. Use LaTeX for all mathematical formulas, units with exponents, and scientific notation {{(e.g., $10^{{-3}} \text{{ kg}}$ or $\text{{m}}^3$)}}.
            
            DOCUMENT:
            {doc}
            
            Return the output as a list of JSON objects with the following structure:
            [
                {{
                    "header": "The section title",
                    "content": "The actual text chunk",
                    "description": "Description of any figures/tables in this chunk",
                    "keywords": ["term1", "term2"],
                    "requires_previous_context": "true or false"
                    "summary": "One sentence context"
                }}
            ]

            Return ONLY the JSON array. Do not include any introductory or concluding text.
            """
        )

chunking_chain = template | llm

def get_chunk_json(chunk_list):
    max_retries = 10
    retry_delay = 5
    
    for i in range(max_retries):
        for chunk in chunk_list:
            try:
                response = chunking_chain.invoke({"doc": chunk})
                content = response.content
                print(f"CONTENT: \n {content}")
            except Exception as e:
                #Need for exception here is because the max number of tokens per minute or TPM is exceeded and requires more time to reload
                if "rate_limit_exceeded" in str(e).lower():
                    print(f"Rate limit hit. Waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    #retry_delay *= 2   Double the wait time for the next try
                else:
                    raise e
    raise Exception("Max retries exceeded")

chunk_json = get_chunk_json(chunk_list)
with open("chunks_json.json", "w") as f:
    json.dump(chunk_json)