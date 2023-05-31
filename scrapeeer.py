import time
from pprint import pprint
import requests
from search_engines import Google
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# 📌TODO
# - Here are the items remaining for using this function. First, we need to update the keyword section to extract that from the search query.
# - We also need to move this to a modular platform so we can easily reuse this with the open ai function.
# - Make the script do the scraping in parallel, especially the contents of each URL so that it will be faster. But the final function should be still synchronous and it should wait for the other three scrapers to finalize their task.
# - Add a proper timeout to ignore pages that takes too long to load.
# - Check if we can use an ingest function to convert the contents of the search results into a vector database and then perform a similar search query before sending that to an LLM. That should make the results better and will require less cost.


nltk.download('punkt')
nltk.download('stopwords')


# If the word is longer than 5 characters, we should include the whole word instead of cutting it.
def get_root_words(query):
    query = re.sub(r"[^a-zA-Z0-9\s]", "", query)  # Remove all non-alphabetic and non-numeric characters
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(query)
    filtered_words = [word for word in words if word not in stop_words]  # filter out stop words
    root_words = [word if len(word) > 8 else stemmer.stem(word) for word in filtered_words]
    return root_words


def remove_fuzzy_duplicates(array, similarity_threshold=80):
    # Initialize an empty list to store the unique items
    unique_items = []

    # Loop through each item in the array
    for item in array:
        # If the item is not similar to any item in unique_items, add it to unique_items
        if not any(fuzz.ratio(item, unique_item) > similarity_threshold for unique_item in unique_items):
            unique_items.append(item)

    return unique_items


def filter_with_adjacent_items(array, query_root_keywords, num_adjacent):
    # Initialize a list to store indices of items containing the keywords
    indices = []

    # Loop through the array to find indices of items containing the keywords
    for i, item in enumerate(array):
        if any(keyword.lower() in item.lower() for keyword in query_root_keywords):
            indices.append(i)

    # Initialize a list to store the final filtered items
    filtered_items = []

    # Add items at the indices found and their adjacent items to the filtered items list
    for index in indices:
        start = max(0, index - num_adjacent)  # Ensure start is not less than 0
        end = min(len(array), index + num_adjacent + 1)  # Ensure end does not exceed the length of the array
        filtered_items.extend(array[start:end])

    return filtered_items


import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import asyncio


async def extract_text(session: ClientSession, url: str, query_root_keywords=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    async with session.get(url, headers=headers) as response:
        html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')

    for script in soup(['script', 'style']):  # remove all javascript and stylesheet code
        script.extract()

    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop blank lines and lines with less than or equal to 5 words
    text = '\n'.join(
        chunk for chunk in chunks if chunk and (0 < len(chunk.split()) < 200 or len(chunk.split()) > 400)).split(
        '\n')

    text = filter_with_adjacent_items(text, query_root_keywords=query_root_keywords, num_adjacent=3)
    text = remove_fuzzy_duplicates(text)

    return text


engine = Google()

# Remove pipes
# Remove utf-8 chars
# Use character count instead of word count.
# Concatenate all the texts from the page 1 result
# If scraping returned empty move on to other one until you have 3
# Revert back to requests, playwright is too slow
# icrease page to 2, and ask the user to open all those with relevant links insteads
query = "BTC to PHP"
keywords = get_root_words(query)
print(keywords)

results = engine.search(query, pages=1)

pprint(results.results())

# Only TOp 3
results_links = results.links()[:5]

pprint(results_links)


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [extract_text(session, link, query_root_keywords=keywords) for link in results_links]
        scrape_results = await asyncio.gather(*tasks)
    return scrape_results


results = asyncio.run(main())

print("done", results)
