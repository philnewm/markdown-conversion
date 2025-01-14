from src import code_block, admonition
from markdown_it import MarkdownIt
from markdown_it.token import Token
from pathlib import Path

import click
import yaml


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("input_file", type=click.STRING)
@click.argument("repo_url", type=click.STRING)
@click.argument("output_file", type=click.STRING)
def insert_code_references(
    input_file: str,
    repo_url: str,
    output_file: str
    ) -> None:

    # Define statics
    export_file: Path = Path(output_file)
    md = MarkdownIt()
    md_content: str = Path(input_file).read_text()
    tokens: list[Token] = md.parse(md_content)
    output_dir = Path("local_tmp")

    # Run logic
    code_refs: list[code_block.CodeReferenceMeta] = code_block.get_code_refs(tokens=tokens)
    download_files: set[Path] = set(code_ref.file_path for code_ref in code_refs)

    for file in download_files:
        code_block.download_file_from(
            base_url=Path(repo_url),
            source=file,
            output=output_dir,
            )
    
    step_to_code_maps: dict[str, dict[str, str]] = code_block.step_to_code_maps(
    files=set(file for file in download_files if file.suffix == ".yml"),
    path=output_dir,
    )

    code_map_list: list[code_block.CodeMap] = code_block.map_reference_to_source(
        code_refs=code_refs,
        path=Path("local_tmp"),
        step_to_code_maps=step_to_code_maps,
        )

    export_content: str = code_block.update_text(md_content, code_map_list)
    export_file.write_text(export_content)

    click.echo(str(export_file))


@cli.command()
@click.argument("input_file", type=click.STRING)
@click.argument("output_file", type=click.STRING)
def replace_admonitions(input_file: str, output_file: str) -> None:

    content: str = Path(input_file).read_text()
    export_file: Path = Path(output_file)

    for admonition_item in admonition.admonitions:
        content: str = content.replace(admonition_item.obsidian, admonition_item.devto)

    export_file.write_text(content)

if __name__ == "__main__":
    print(cli.commands)
    cli()