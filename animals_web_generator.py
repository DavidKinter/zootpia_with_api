"""
Animals Web Generator Module

This module fetches animal data from Animals API and generates an HTML page
displaying the information in a card-based layout. It handles user input
validation, API communication, data processing, and HTML generation.
"""
import os
import re
from typing import Dict, Optional, Any, List

import requests
from dotenv import load_dotenv
from unidecode import unidecode

# Load environment variables from .env file
load_dotenv()

# API-specific constants
# 'Optional' = Value can either be the specified type or None (if error occurs)
KEY: Optional[str] = os.environ.get("API_NINJA_KEY")  # Get API key from .env
BASE_URL: str = "https://api.api-ninjas.com/v1/"
REQUEST_TIMEOUT_SECONDS: int = 10

# HTML output-specific constants
ANIMALS_TEMPLATE_FILE: str = "animals_template.html"
OUTPUT_HTML_FILE: str = "animals.html"
DEFAULT_NA_VALUE: str = "N/A"
HTML_PLACEHOLDER_TEXT: str = "__REPLACE_ANIMALS_INFO__"


def get_input(prompt="Enter animal name: ") -> str:
    """
    Gets input and validates it using extended Latin regex, where
        r' =                Raw string
        ^ =                 Beginning of the string
        r'^[a-zA-ZÀ-ÿĀ-žǍ-ǰȀ-ȳḀ-ỿ -]*$' = Allowed ext. Latin chars, " ", "-"
        * =                 Zero or more of the preceding characters
        $ =                 End of the string
    """
    # Extended Latin character set for input validation with RegEX
    allowed_chars = r'^[a-zA-ZÀ-ÿĀ-žǍ-ǰȀ-ȳḀ-ỿ -]*$'
    while True:
        raw_input = input(prompt).strip()
        if not raw_input:  # Check for empty input
            print("Error: Animal name cannot be empty.")
            continue  # skips rest of loop iteration, jumps back to beginning
        if re.match(allowed_chars, raw_input):  # RegEx validation
            return raw_input
        print("Error: Only letters, spaces, and dashes are allowed.")


def fetch_api_data(
        endpoint: str,
        animal_name: str,
        params: Optional[Dict[str, Any]] = None
        ) \
        -> Optional[Dict[str, Any]]:  # None on error, or if no data available
    """
    Generic function to fetch data from the Animals API
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
        -> Optional[List[Dict[str, Any]]]:  # None: error or data not available
    """
    Fetches animal data from Animals API and returns a list of animal dicts
    """
    print(f"\nFetching animal data for '{animal_name.title()}' from API...")
    data = fetch_api_data("animals", animal_name)
    if data is None:
        return None
    return data  # No animals found = [] else [...] (with data)


def process_input(raw_input: str) -> str:
    """
    Takes 'raw_input', transliterates special characters to closest ASCII
    character with 'unidecode', and normalizes input
    """
    # Convert to ASCII, strip whitespace, and convert to lowercase
    processed_input = unidecode(raw_input).strip().lower()
    return processed_input


def load_html_template(file_path: str = ANIMALS_TEMPLATE_FILE) \
        -> Optional[str]:
    """
    Loads HTML template from file and returns it as a string.
    Returns None if file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="UTF-8") as handle:
            html_str = handle.read()
        return html_str
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except IOError:
        print(f"Error: Could not read file at {file_path}")
        return None


def format_value(value_str: Any) -> str:
    """
    Helper function. Checks if 'value_str' is a string and capitalizes all
    words in it, unless it is "N/A" (DEFAULT_NA_VALUE). If it is "N/A",
    the function returns the original 'value_str' unchanged. The function
    makes sure all items from the API response are properly, and identically,
    formatted.
    """
    if (isinstance(value_str, str)  # Checks if 'value_str' is type(str)
            and value_str.lower() != DEFAULT_NA_VALUE.lower()):
        title_cased_str = value_str.title()
        # Correct apostrophe followed by 'S' (for Darwin's Fox)
        return title_cased_str.replace("’S", "’s")
    return str(value_str) if value_str is not None else DEFAULT_NA_VALUE


def extract_animal_data(animal_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Helper function. Takes a raw animal data dictionary from the API,
    extracts and formats relevant details, and returns them as a new
    dictionary for the HTML template.
    """
    # Safely extract data for individual animal
    animal_name = animal_data.get("name", DEFAULT_NA_VALUE)

    # Get first location from locations list, or use default
    locations_list = animal_data.get("locations")
    if locations_list and isinstance(locations_list, list):
        animal_location = locations_list[0]
    else:
        animal_location = DEFAULT_NA_VALUE

    # Extract characteristics safely
    characteristics = animal_data.get("characteristics", {})
    animal_diet = characteristics.get("diet", DEFAULT_NA_VALUE)
    animal_type = characteristics.get("type", DEFAULT_NA_VALUE)

    # Formats extracted data and returns it as dictionary
    return {
        "name":     format_value(animal_name),
        "diet":     format_value(animal_diet),
        "location": format_value(animal_location),
        "type":     format_value(animal_type)
        }


def process_animals_data(data: Optional[List[Dict[str, Any]]]) \
        -> List[Dict[str, str]]:
    """
    Takes API data and returns list of dicts with each animal's formatted
    'name', 'diet', 'first location from the locations list', and 'type'
    """
    if data is None:  # API error occurred - treat same as "no animals found"
        return []  # Empty list to prevent subsequent errors
    animals_list = []
    # Iterates through API data, extracts items, and creates new list of dicts
    for animal in data:
        processed_animal_dict = extract_animal_data(animal)
        animals_list.append(processed_animal_dict)
    return animals_list


def create_animal_html_card(animal_obj: Dict[str, str]) -> str:
    """
    Helper function. Takes a processed animal dict object and returns
    an HTML string representing a single animal card item.
    """
    return (
        f"<li class='cards__item'>"
        f"<div class='card__title'>{animal_obj['name']}</div>"
        f"<p class='card__text'>"
        f"<strong>Diet:</strong> {animal_obj['diet']}<br/>"
        f"<strong>Location:</strong> {animal_obj['location']}<br/>"
        f"<strong>Type:</strong> {animal_obj['type']}<br/>"
        f"</p>"
        f"</li>"
    )


def generate_animals_html_content(
        data: Optional[List[Dict[str, Any]]],
        animal_name: str
        ) -> str:
    """
    Creates HTML content string from API data by processing each animal
    and combining their HTML card representations. If no animals found,
    returns a styled error message.
    """
    animals_list = process_animals_data(data)
    # Check if no animals were found (empty list)
    if len(animals_list) == 0:
        return (
            f'<h2 style="'
            f'text-align: center; '
            f'font-size: 30pt; '
            f'font-weight: normal;"'
            f'>'
            f'The animal "{animal_name.title()}" does not exist.'
            f'</h2>'
        )
    # Generate HTML cards for found animals
    animal_html_cards = []
    for animal_obj in animals_list:
        animal_html_cards.append(create_animal_html_card(animal_obj))
    return "\n\n".join(animal_html_cards)


def create_final_html(
        data: Optional[List[Dict[str, Any]]],
        animal_name: str
        ) -> str:
    """
    Generates complete HTML content by inserting animal data into the
    placeholder '__REPLACE_ANIMALS_INFO__' in 'animals_template.html'
    This function first loads the base HTML template and retrieves a
    formatted string of relevant animal details. If the placeholder is not
    found in the template, an empty string is returned.
    """
    # Load HTML template file
    html_template = load_html_template()
    if html_template is None:  # Error reading template file
        print(
            "Error: HTML template could not be loaded. "
            "Cannot create updated HTML."
            )
        return ""  # If no content -> function's contract is to return str

    # Generate HTML content for animals and insert into template
    animals_html_content = generate_animals_html_content(data, animal_name)
    if HTML_PLACEHOLDER_TEXT in html_template:
        return html_template.replace(
            HTML_PLACEHOLDER_TEXT, animals_html_content
            )
    print(
        f"Warning: Placeholder '{HTML_PLACEHOLDER_TEXT}' not "
        f"found in template"
        )
    return ""  # If no content -> function's contract is to return str


def save_html_to_file(
        html_content: str,
        file_path: str = OUTPUT_HTML_FILE
        ) -> bool:
    """
    Saves the provided HTML string to the specified file.
    This function will create the file if it does not exist,
    or overwrite it if it does. Returns True on success, False on failure.
    """
    # Handles empty string from create_final_html
    if not html_content:  # If no HTML content was created
        print("No HTML content provided to save. File will not be written.")
        return False  # Indicates failure or no action
    try:
        with open(file_path, "w", encoding="UTF-8") as handle:
            handle.write(html_content)
        print(f"Successfully saved updated HTML to {file_path}")
        return True  # Indicates success
    except IOError as e:
        print(f"Error: Could not write to file at {file_path}. Reason: {e}")
        return False  # Indicates failure


def main():
    """
    Main program:
    Gets user input for animal name, fetches animal data from Animals API,
    generates an HTML representation, and saves it to 'animals.html'.
    """
    # Gets user input and fetches animal data from API
    raw_input = get_input()
    animal_name = process_input(raw_input)
    data = fetch_animals_data(animal_name)

    # Generates HTML content and saves it to file
    final_html = create_final_html(data, animal_name)
    if final_html:
        save_html_to_file(final_html)
    else:
        print(
            f"HTML content generation failed or resulted in empty content. "
            f"Skipping save to {OUTPUT_HTML_FILE}."
            )


if __name__ == '__main__':
    main()
