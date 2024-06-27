from typing import List, Any, Dict
import json
import re

def read_file(file_path: str) -> List[str]:
    """
    Reads the contents of a file and returns a list of strings, each representing a line in the file.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        List[str]: A list of strings, each representing a line in the file.
    """
    lines = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    
    return lines

def json_string_to_json(json_string: str) -> Any:
    """
    Converts a JSON string into a JSON object.

    Args:
        json_string (str): The JSON string to be converted.

    Returns:
        Any: The resulting JSON object (usually a dict or list).
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the JSON string: {e}")
        return None
    
    
def extract_json_from_string(input_string: str) -> Dict[str, Any]:
    """
    Extracts JSON content from a string that contains JSON data embedded within it.

    Args:
        input_string (str): The input string containing JSON data.

    Returns:
        Dict[str, Any]: The parsed JSON content as a dictionary.
    """
    # Regular expression to match JSON content
    # json_regex = re.compile(r'```json\n({.*?})\n```', re.DOTALL)
    
    pattern = r'```(\w+)\n({.*?})\n```'
    json_regex = re.compile(pattern, re.DOTALL)
    
    # Search for JSON content within the input string
    match = json_regex.search(input_string)
    
    if not match:
        raise ValueError("No JSON content found in the input string.")
    
    # Extract JSON content
    # json_content = match.group(1)
    json_content = match.group(2)
    
    # Parse JSON content
    parsed_json = json.loads(json_content)
    
    return parsed_json

def main():
    file_path = 'example.txt'  # Replace with your file path
    lines = read_file(file_path)
    
    if lines:
        for line in lines:
            print(line.strip())

if __name__ == "__main__":
    main()
