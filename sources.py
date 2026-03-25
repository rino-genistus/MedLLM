import requests
from bs4 import BeautifulSoup

# Get a specific book page
response = requests.get(
    "https://openstax.org/books/anatomy-and-physiology-2e/pages/",
    headers={"User-Agent": "Mozilla/5.0"}
)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the main content
content = soup.find('div', {'data-type': 'page'})
if content:
    print(content.get_text(separator='\n', strip=True))