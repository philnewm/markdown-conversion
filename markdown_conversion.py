from src.code_block import (
    download_files,
    extract_code_refs,
    CodeReferenceMeta,
    get_workflow_code,
    map_reference_to_source,
    CodeMap,
    update_text,
)
from src.file_io import PathHandler
from pathlib import Path

import os
import click


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("input_files", type=click.STRING)
def download(input_files: str) -> None:
    input_file_list: list[str] = input_files.split(",")
    download_files(url_list=input_file_list, output_dir=Path(f"local_tmp"), sub_dir=True)

    for input_file in input_files.split(","):
        path_handler = PathHandler(file_path=input_file, local_tmp="local_tmp", gh_url=True)
        code_references: list[CodeReferenceMeta] = extract_code_refs(md_file_path=f"{path_handler.local_tmp}/{path_handler.file_name}")

        ref_paths: set[str] = set(str(code_ref.file_path) for code_ref in code_references)
        ref_urls: list[str] = [f"{path_handler.repo_root}/{ref_path}" for ref_path in ref_paths]
        print(f"{path_handler.repo_root=}")
        download_files(url_list=ref_urls, output_dir=Path(path_handler.local_resources))


@cli.command()
@click.argument("output_dir", type=click.STRING)
def insert_code_references(
    output_dir: str
    ) -> None:

    data_dirs: list[str] = os.listdir("local_tmp")

    for data_dir in data_dirs:
        markdown_file: str = f"local_tmp/{data_dir}/{data_dir}.md"
        path_handler = PathHandler(file_path=markdown_file, local_tmp="local_tmp", gh_url=False)

        code_references: list[CodeReferenceMeta] = extract_code_refs(md_file_path=path_handler.local_markdown)
        code_map_list: list[CodeMap] = map_reference_to_source(code_refs=code_references, path=Path(path_handler.local_resources), data_dir=data_dir)
        export_text: str = update_text(source_file=path_handler.local_markdown, code_map_list=code_map_list)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print(f"{output_dir}/{data_dir}.md")
        Path(f"{output_dir}/{data_dir}.md").write_text(export_text)


@cli.command()
@click.argument("input_file", type=click.STRING)
@click.argument("output_file", type=click.STRING)
def replace_admonitions(input_file: str, output_file: str) -> None:

    content: str = Path(input_file).read_text()
    export_file: Path = Path(output_file)

    for admonition_item in admonition.admonitions:
        content: str = content.replace(admonition_item.obsidian, admonition_item.devto)

    export_file.parent.mkdir(parents=True, exist_ok=True)
    export_file.write_text(content)

if __name__ == "__main__":
    cli()
