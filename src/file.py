def read_file(file_path: str) -> str:
    """Read a text file

    Args:
        input_file (str): Path to file

    Returns:
        str: file content
    """

    with open(file_path, "r") as file:
        content: str = file.read()
    
    return content


def write_file(file_path: str, content: str) -> None:
    """Write a text file

    Args:
        file_path (str): Path to write to
        content (str): Content to write
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)