import requests
from bs4 import BeautifulSoup
import os
import io
import pdfplumber


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

for name, url in chosen_books.items():
    response = requests.get(url)
    os.makedirs(os.path.join("DIAGRAMS", name))
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        with open(f"TEXTBOOKS/{name}.txt", "w") as f:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    f.write(text + "\n\n")
                for i, image in enumerate(page.images):
                    x0 = max(0, image['x0'])
                    top = max(0, image['top'])
                    x1 = min(page.width, image['x1'])
                    bottom = min(page.height, image['bottom'])

                    if x1 > x0 and bottom>top:
                        bbox = (x0, top, x1, bottom)
                        cropped_page = page.within_bbox(bbox)
                        img = cropped_page.to_image(resolution=300)
                        img.save(f"DIAGRAMS/{name}/page_{page.page_number}_img_{i+1}.png")

# Get a specific book page
response = requests.get(
    "https://openstax.org/books/anatomy-and-physiology-2e/pages/1-introduction",
    headers={"User-Agent": "Mozilla/5.0"}
)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the main content
content = soup.find('div', {'data-type': 'page'})
if content:
    print(content.get_text(separator='\n', strip=True))