import os

from urllib.parse import ParseResult, urlparse

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

class PathHandler():
    def __init__(self, file_path: str, local_tmp: str) -> None:

        self.file_name: str = os.path.basename(file_path)
        self.file_name_raw: str = os.path.splitext(self.file_name)[0]
        self.local_tmp: str = f"{local_tmp}/{self.file_name_raw}"
        self.local_resources: str = f"{local_tmp}/{self.file_name_raw}/resources"
        self.repo_root: str = self.extract_repo_root(file_path)

    def extract_repo_root(self, url: str) -> str:
        """Extracts the repository root including the branch name from a raw.githubusercontent.com URL.
        """

        parsed_url: ParseResult = urlparse(url)
        parts: list[str] = parsed_url.path.strip("/").split("/")

        if len(parts) < 5:
            raise ValueError("URL does not match expected GitHub raw format.")
        
        # Extract the repository root (including branch name)
        user, repo, _, _, branch = parts[:5]
        repo_root: str = f"https://raw.githubusercontent.com/{user}/{repo}/refs/heads/{branch}"
        
        return repo_root
