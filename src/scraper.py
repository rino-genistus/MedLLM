import io
import os
import pdfplumber
import requests


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

remaining_textbooks = {
    #"Biology2e": "https://d3bxy9euw4e147.cloudfront.net/oscms-prodcms/media/documents/Biology2e-OP_aHSFm3Y.pdf",
    #"Human Osteology": "https://scholarworks.gvsu.edu/cgi/viewcontent.cgi?article=1004&context=books",
    #"General Microbiology": "/Users/rino/Downloads/General-Microbiology-1774571417.pdf",
    #"College Physics 2e": "https://assets.openstax.org/oscms-prodcms/media/documents/College_Physics_2e-WEB_7Zesafu.pdf",
    #"Statistical Inference for Everyone": "/Users/rino/Downloads/Statistical Inference For Everyone.pdf",
    "Orgo with Bio": "https://digitalcommons.morris.umn.edu/cgi/viewcontent.cgi?article=1000&context=chem_facpubs",
}
def create_dir():
    os.makedirs("DIAGRAMS", exist_ok=True)
    os.makedirs("TEXTBOOKS", exist_ok=True)

def create_text_and_images(books):
    for name, url in books.items():
        headers = {'User-Agent': 'Mozilla/5.0'}
        if url.startswith("/") or url[1] == ":": 
            pdf_data = io.BytesIO(open(url, "rb").read())
        else:
            pdf_data = io.BytesIO(requests.get(url, headers=headers).content)
        with pdfplumber.open(pdf_data) as pdf:
            with open(f"data/processed/TEXTBOOKS/{name}.txt", "w") as f:
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