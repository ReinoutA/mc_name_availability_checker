import logging
import asyncio
import string
import sys
import random
import aiohttp
import nltk
from nltk.corpus import wordnet

# Ensure the wordnet corpus is available
nltk.download('wordnet')

# Constants
NAME_LENGTH = 7
WORDS_PER_REQUEST = 10
LANGUAGE = 'en'
SEM_LIMIT = 40
API_RETRIES = 10000

print_non_dict_words = False

# API Endpoints
API_OPTIONS = {
    "word_api1": f'https://random-word-api.herokuapp.com/word?number={WORDS_PER_REQUEST}&length={NAME_LENGTH}&lang={LANGUAGE}',
    "word_api2": f"https://random-word-form.herokuapp.com/random/noun/a?count={WORDS_PER_REQUEST}"
}

AVAILABILITY_API_OPTIONS = [
    "https://api.mojang.com/users/profiles/minecraft/{}",
    "https://api.ashcon.app/mojang/v2/user/{}"
]

def is_valid_word(word):
    """Check if the word is a valid dictionary word."""
    return bool(wordnet.synsets(word))

async def fetch_random_words(session, api_choice):
    """Fetch random words using the selected API."""
    response = await session.get(API_OPTIONS[api_choice])
    words = await response.json()
    return words

async def check_name_availability(name, session, sem, api_choice):
    """Check if a name is available using the selected availability API."""
    availability_api = AVAILABILITY_API_OPTIONS[api_choice].format(name)

    async with sem, session.get(availability_api) as resp:
        if resp.status in {204, 404}:  # Name is available
            is_dict_word = is_valid_word(name)
            if is_dict_word or print_non_dict_words:
                return 200, name, is_dict_word
        return resp.status, name, None  # Name is taken or not printed

async def generate_words(session, mode, max_len, api_choice):
    """Generate a list of words or random strings based on the mode."""
    if mode == "words":
        words = await fetch_random_words(session, api_choice)
    else:
        words = [
            ''.join(random.choice(string.ascii_uppercase + string.digits + "_")
                    for _ in range(max_len)) for _ in range(WORDS_PER_REQUEST)
        ]
    return words

async def main(max_len=NAME_LENGTH, mode="words", word_api_choice="word_api1", availability_api_choice=0):
    """Main function to coordinate the checking of name availability."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("log.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger()

    sem = asyncio.Semaphore(SEM_LIMIT)

    async with aiohttp.ClientSession() as session:
        for _ in range(API_RETRIES):
            words = await generate_words(session, mode, max_len, word_api_choice)
            tasks = [asyncio.create_task(check_name_availability(word, session, sem, availability_api_choice)) for word
                     in words]
            results = await asyncio.gather(*tasks)

            for status, name, is_dict_word in results:
                if status == 200:
                    if is_dict_word:
                        logger.info(f"'{name}' is available and is a valid dictionary word.")
                    elif is_dict_word is False:
                        logger.info(f"'{name}' is available but is not a dictionary word.")
                elif status == 400:
                    logger.warning(f"'{name}': Bad request.")
                elif status == 404:
                    if is_dict_word:
                        logger.info(f"'{name}' is available and is a valid dictionary word.")
                    elif is_dict_word is False:
                        logger.info(f"'{name}' is available but is not a dictionary word.")
                else:
                    logger.debug(f"Unexpected status: {status} for name: '{name}'")

if __name__ == '__main__':
    asyncio.run(main(word_api_choice="word_api1", availability_api_choice=0))
