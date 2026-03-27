from src.scraper import create_text_and_images, create_dir, books, chosen_books
from src.processor import get_useable_chunks, get_chunk_json

""" 
    Used to Create the Directory for the textbooks' text files and the diagrams from the those respective text files. Only ran this code
    on the Chemistry textbook for testing purposes and MVP. 
"""
#create_dir()
#create_text_and_images(chosen_books)

"""
    Used these lines to create the JSON file needed for vector database and the metadata for passing it to the database itself.
"""
#chunks_to_feed = get_useable_chunks()
#chunks_in_json = get_chunk_json(chunks_to_feed)