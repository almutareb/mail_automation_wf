from typing import List, Any
import json

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

def main():
    file_path = 'example.txt'  # Replace with your file path
    lines = read_file(file_path)
    
    if lines:
        for line in lines:
            print(line.strip())

if __name__ == "__main__":
    main()
