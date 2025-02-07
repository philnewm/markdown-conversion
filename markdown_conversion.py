from src.code_block import download_files, extract_code_refs, CodeReferenceMeta
from src.file_io import PathHandler
from markdown_it import MarkdownIt
from markdown_it.token import Token
from pathlib import Path

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
        path_handler = PathHandler(file_path=input_file, local_tmp="local_tmp")
        code_references: list[CodeReferenceMeta] = extract_code_refs(md_file_path=f"{path_handler.local_tmp}/{path_handler.file_name}")

        ref_paths: set[str] = set(str(code_ref.file_path) for code_ref in code_references)
        ref_urls: list[str] = [f"{path_handler.repo_root}/{ref_path}" for ref_path in ref_paths]

        download_files(url_list=ref_urls, output_dir=Path(path_handler.local_resources))


@cli.command()
@click.argument("input_files", type=click.STRING)
@click.argument("output_files", type=click.STRING)
def insert_code_references(
    input_file: str,
    output_file: str
    ) -> None:

    # Define statics
    export_file: Path = Path(output_file)

    md = MarkdownIt()
    md_content: str = Path(constants.download_dir / input_file.lstrip("/")).read_text()
    tokens: list[Token] = md.parse(md_content)

    # Run logic
    code_refs: list[code_block.CodeReferenceMeta] = code_block.get_code_refs(tokens=tokens)
    code_files: set[Path] = set(code_ref.file_path for code_ref in code_refs)
    workflow_files: list[Path] = [file for file in code_files if file.parent.name == constants.workflow_directory]

    workflow_code: dict[str, str] = code_block.get_workflow_code(
        files=workflow_files,
        path=constants.download_dir,
        )

    code_map_list: list[code_block.CodeMap] = code_block.map_reference_to_source(
        code_refs=code_refs,
        path=constants.download_dir,
        step_to_code_maps=workflow_code,
        )

    export_text: str = code_block.update_text(md_content, code_map_list)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    export_file.write_text(export_text)


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
