# Minecraft Username Availability Checker

This Python script asynchronously fetches random words, checks if they are valid English dictionary words, and verifies their availability as Minecraft usernames using the Mojang API.

## Features

- **Random Word Generation**: Fetches random words from APIs.
- **Username Availability Check**: Uses Mojang and Ashcon APIs to check if a Minecraft username is available.
- **Dictionary Check**: Verifies if a username is a valid dictionary word using NLTK's WordNet.
- **Asynchronous Execution**: Utilizes `asyncio` for efficient concurrent operations.

## Installation

1. Clone this repository.
2. Install the required Python libraries:

   ```sh
   pip install aiohttp nltk
