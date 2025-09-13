import streamlit as st
from scrape_ingredients import IngredientExtractor

st.title("Recipe Ingredient Extractor")

st.write("Paste one or more recipe URLs (one per line):")
urls_input = st.text_area("Recipe URLs", height=200, placeholder="https://example.com/recipe1\nhttps://example.com/recipe2")

extractor = IngredientExtractor()

if st.button("Parse"):
    urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
    results = []
    for url in urls:
        title, url_out, ingredients = extractor.extract_ingredients(url)
        result = extractor.post_process(title, url_out, ingredients)
        results.append(result)
    output_text = "\n\n".join(results)
    st.text_area("Parsed Ingredients", value=output_text, height=400)