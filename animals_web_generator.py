"""
Animals Web Generator Module

This module processes animal data and generates an HTML page displaying
the information in a card-based layout. It handles user input validation,
data processing, and HTML generation.
"""

import re
from typing import Dict, Optional, Any, List

from unidecode import unidecode

import data_fetcher as df

# --- Module Constants ---
ANIMALS_TEMPLATE_FILE: str = "animals_template.html"
OUTPUT_HTML_FILE: str = "animals.html"
DEFAULT_NA_VALUE: str = "N/A"
HTML_PLACEHOLDER_TEXT: str = "__REPLACE_ANIMALS_INFO__"

# Regex for input validation (Detailed description see 'get_input' docstring)
INPUT_VALIDATION_REGEX: str = r'^[a-zA-ZÀ-ÿĀ-žǍ-ǰȀ-ȳḀ-ỿ -]*$'

# Inline styles for "no animals found" message
NO_ANIMALS_FOUND_STYLE: str = (
    'text-align: center;'
    'font-size: 30pt;'
    'font-weight: normal;'
)


def get_input(
        prompt: str = "Enter animal name: "
        ) -> str:  # Default prompt value
    """
    Gets input and validates it using extended Latin regex, where
    r' =                Raw string
    ^ =                 Beginning of the string
    r'^[a ... -]*$' =   Allowed extended Latin characters, incl. " ", "-"
    * =                 Zero or more of the preceding characters
    $ =                 End of the string
    """
    while True:
        raw_input = input(prompt).strip()
        if not raw_input:  # Check for empty input
            print("Error: Animal name cannot be empty.")
            continue  # skips rest of loop iteration, jumps back to beginning
        if re.match(INPUT_VALIDATION_REGEX, raw_input):  # RegEx validation
            return raw_input
        print("Error: Only letters, spaces, and dashes are allowed.")


def process_input(raw_input: str) -> str:
    """
    Takes 'raw_input', transliterates special characters to closest ASCII
    character with 'unidecode', and normalizes input to lowercase.
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
    Helper function. Formats values for display by capitalizing words,
    unless the value is "N/A" (DEFAULT_NA_VALUE). If it is "N/A",
    returns the original value unchanged. Ensures all items from the
    API response are properly and identically formatted.
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
    extracts and formats relevant details (name, diet, location, type),
    and returns them as a new dictionary ready for HTML template insertion.
    """
    # Safely extract data for individual animal
    animal_name = animal_data.get("name", DEFAULT_NA_VALUE)

    # Get first location from locations list, or use default
    locations_list = animal_data.get("locations")
    if (locations_list  # Check if list is not empty
            and isinstance(locations_list, list)
            and locations_list):
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
    Takes raw animal data from API and returns list of dictionaries with
    each animal's formatted 'name', 'diet', 'first location from the
    locations list', and 'type'. Returns empty list if data is None.
    """
    if data is None:  # Data fetching error - treat same as "no animals found"
        return []  # Empty list to prevent subsequent errors
    animals_list = []
    # Iterates through animal data, extracts items, creates new list of dicts
    for animal in data:
        processed_animal_dict = extract_animal_data(animal)
        animals_list.append(processed_animal_dict)
    return animals_list


def create_animal_html_card(animal_obj: Dict[str, str]) -> str:
    """
    Helper function. Takes a processed animal dictionary object and returns
    an HTML string representing a single animal card item for display.
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


def generate_no_animals_message(animal_name: str) -> str:
    """
    Helper function. Creates a styled HTML error message when no animals
    are found for the given animal name.
    """
    return (
        f'<h2 style="{NO_ANIMALS_FOUND_STYLE}">\n'  # Using the constant
        f'The animal "{animal_name.title()}" does not exist.'
        f'</h2>'
    )


def generate_animals_html_content(
        data: Optional[List[Dict[str, Any]]],
        animal_name: str
        ) -> str:
    """
    Creates HTML content string from animal data by processing each animal
    and combining their HTML card representations. If no animals found,
    returns a styled error message instead.
    """
    animals_list = process_animals_data(data)
    # Check if no animals were found (empty list)
    if not animals_list:
        return generate_no_animals_message(animal_name)

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
    Generates complete HTML content by loading the template file and
    inserting animal data into the placeholder '__REPLACE_ANIMALS_INFO__'.
    Returns empty string if template cannot be loaded or placeholder not found.
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
        print(f"Saved updated HTML to {file_path}")
        return True  # Indicates success
    except IOError as e:
        print(f"Error: Could not write to file at {file_path}. Reason: {e}")
        return False  # Indicates failure


def main():
    """
    Main program flow:
    1. Gets user input for animal name and validates it
    2. Processes input (normalizes to lowercase ASCII)
    3. Fetches animal data from Animals API via data_fetcher module
    4. Generates HTML content by inserting data into template
    5. Saves final HTML to 'animals.html' file
    """
    # Gets input, processes it, fetches animal data from API via 'data_fetcher'
    raw_input = get_input()
    animal_name = process_input(raw_input)
    data = df.fetch_animals_data(animal_name)
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
