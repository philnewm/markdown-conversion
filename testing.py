from pathlib import Path
from src.code_block import download_files

source_list: list[str] = [
    "https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/README.md",
    "https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/TODO.md",
    "https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/.gitignore",
]

download_files(url_list=source_list, output_dir=Path("local_tmp"))
