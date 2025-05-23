"""
Data Fetcher Module

This module is responsible for fetching animal data from Animals API.
It handles API communication, error handling, and returns the raw data
or appropriate error indicators.
"""
import os
from typing import Dict, Optional, Any, List

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API-specific constants
# 'Optional' = Value can either be the specified type or None (if error occurs)
KEY: Optional[str] = os.environ.get("API_NINJA_KEY")  # Get API key from .env
BASE_URL: str = "https://api.api-ninjas.com/v1/"
REQUEST_TIMEOUT_SECONDS: int = 10  # Timeout for API requests in seconds


def fetch_api_data(
        endpoint: str,
        animal_name: str,
        params: Optional[Dict[str, Any]] = None
        ) \
        -> Optional[List[Dict[str, Any]]]:  # None on error, data if successful
    """
    Generic function to fetch data from the Animals API.
    Returns None on error (network issues, API key missing, etc.),
    or the API response data (list of dictionaries) if successful.
    Empty list means no animals found but request was successful.
    """
    if params is None:
        params = {}
    if not KEY:  # Check if API key is available
        print(
            "Error: Animals API key is missing. Please check your .env file."
            )
        return None
    headers = {'X-Api-Key': KEY}
    params["name"] = animal_name
    api_url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS
            )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()  # No animals found = [] else [...] (with data)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch data from API: {e}")
        return None


def fetch_animals_data(animal_name: str) \
        -> Optional[List[Dict[str, Any]]]:  # None on error, list if successful
    """
    Fetches animal data from Animals API for the specified animal name.
    Returns None if there was an API error (network, authentication, etc.),
    or a list (empty if no animals found, populated if animals exist).
    """
    print(f"\nFetching animal data for '{animal_name.title()}' from API...")
    data = fetch_api_data("animals", animal_name)
    if data is None:  # Indicates fetch error
        return None
    if not data:  # Empty list from API (no animals found)
        print(f"No data found for '{animal_name.title()}' in the API.")
        return []  # Return empty list to signify "found nothing"
    print(
        f"Successfully fetched {len(data)} entry/entries "
        f"for '{animal_name.title()}'."
        )
    return data


def main():
    """
    Test function for fetching data for a predefined animal.
    Attempts to fetch data and prints the result or an error message.
    Used for module testing and debugging purposes.
    """
    test_animal = "Fox"

    print("\n--- Running data_fetcher.py main() test ---")
    print(f"Attempting to fetch data for: '{test_animal}'")
    data = fetch_animals_data(test_animal)

    if data:
        print(f"\nSuccessfully fetched data for '{test_animal}':")
        for animal in data:
            name = animal.get('name', 'N/A')
            print(f"{name}")
    elif data == []:
        print(
            f"\nNo data found for '{test_animal}' "
            f"(animal may not exist in the API)."
            )
    else:
        print(
            f"\nFailed to fetch data for '{test_animal}'. "
            f"Check API error messages."
            )

    print("\n--- End of data_fetcher.py main() test ---")


if __name__ == '__main__':
    main()
