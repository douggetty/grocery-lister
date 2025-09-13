from recipe_scrapers import scrape_me
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from typing import Tuple, List, Optional


class IngredientExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com"
        }

    def extract_ingredients_scraper(self, url: str)  -> Tuple[Optional[str], List[str]]:
        """Attempt to extract ingredients using the recipe_scraper library."""
        try:
            scraper = scrape_me(url)
            title = scraper.title()
            ingredients = scraper.ingredients()
            return title, ingredients
        except Exception as e:
            print(f"Error using recipe_scraper for {url}: {e}")
            return None, []

    def extract_ingredients_fallback(self, url: str) -> Tuple[Optional[str], List[str]]:
        """Attempt to extract ingredients using JSON-LD schema."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")

            for script in scripts:
                try:
                    data = json.loads(script.string)

                    # Case: @graph structure
                    if isinstance(data, dict) and "@graph" in data:
                        for entry in data["@graph"]:
                            if entry.get("@type") == "Recipe":
                                title = entry.get("name", "Unknown Recipe")
                                ingredients = entry.get("recipeIngredient", [])
                                return title, ingredients

                    # Case: List of schema objects
                    elif isinstance(data, list):
                        for entry in data:
                            if entry.get("@type") == "Recipe":
                                title = entry.get("name", "Unknown Recipe")
                                ingredients = entry.get("recipeIngredient", [])
                                return title, ingredients

                    # Case: Direct Recipe
                    elif isinstance(data, dict) and data.get("@type") == "Recipe":
                        title = data.get("name", "Unknown Recipe")
                        ingredients = data.get("recipeIngredient", [])
                        return title, ingredients

                except (json.JSONDecodeError, TypeError) as e:
                    print(f"JSON parsing error for {url}: {e}")
                    continue

        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")

        return None, []

    def extract_ingredients_from_html(self, url: str) -> Tuple[Optional[str], List[str]]:
        """Attempt to extract ingredients by scraping raw HTML."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string.strip()

            # Select <li> elements inside the correct <ul> class
            ingredients = [
                li.get_text(strip=True)
                for li in soup.select("ul.ingredients-list li")
            ]

            return title, ingredients

        except Exception as e:
            print(f"Error scraping raw HTML for {url}: {e}")
            return None, []

    def extract_ingredients(self, url: str) -> Tuple[str, str, List[str]]:
        """
        Attempts to extract recipe title and ingredients using multiple methods.
        Tries the following in order:
        1. recipe_scraper library
        2. JSON-LD schema fallback
        3. Raw HTML scraping
        """
        title, ingredients = self.extract_ingredients_scraper(url)
        if title and ingredients:
            return title, url, ingredients

        title, ingredients = self.extract_ingredients_fallback(url)
        if title and ingredients:
            return title, url, ingredients

        title, ingredients = self.extract_ingredients_from_html(url)
        if title and ingredients:
            return title, url, ingredients

        return "Unknown Recipe", []
    
    def post_process(self, title: str, url: str, ingredients: List[str]) -> str:
        """
        Formats the recipe title and ingredients into a bulleted text list.
        """
        if not ingredients:
            return f"{title}\nNo ingredients found."

        formatted_ingredients = "\n".join(f"- {ingredient}" for ingredient in ingredients)
        return f"{title}\nURL: {url}\n{formatted_ingredients}"


# # Example usage
# if __name__ == "__main__":
#     extractor = IngredientExtractor()

#     urls = [
#         "https://damndelicious.net/2025/02/28/instant-pot-white-chicken-chili/",  # not currently supported
#         "https://ohsnapmacros.com/lasagna-pasta-skillet/",
#         "https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/",
#         "https://www.skinnytaste.com/korean-beef-rice-bowls/",
#         "https://www.budgetbytes.com/one-pot-chicken-and-rice/",
#         "https://nourishedbynic.com/breakfast-protein-biscuits/",
#         "https://thecleaneatingcouple.com/healthy-buffalo-chicken-dip/",
#         "https://dishingouthealth.com/white-bean-soup/",
#         "https://barefootcontessa.com/recipes/chicken-in-a-pot/",
#         "https://recipe30.com/perfect-pan-seared-salmon-with-lemon-butter-cream-sauce.html/"  # not handled, needs HTML scraped by hand
#     ]

#     for url in urls:
#         title, url, ingredients = extractor.extract_ingredients(url)
#         formatted_output = extractor.post_process(title, url, ingredients)
#         print(formatted_output)
#         print("-" * 40)        