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
@click.argument("output_file", type=click.STRING)
def insert_code_references(
    input_file: str,
    workflow_path: str,
    output_file: str
    ) -> None:

    export_file: Path = Path(output_file)

    md = MarkdownIt()
    md_content: str = Path(input_file).read_text()
    tokens: list[Token] = md.parse(md_content)

    code_refs: list[code_block.CodeReferenceMeta] = code_block.get_code_refs(tokens=tokens)

    step_to_code_map:dict[str, str] = {}

    for code_ref in code_refs:
        if code_ref.file_path.name.endswith(".yml"):
            step_to_code_map = code_block.map_step_name_to_code(
                    gh_workflow=yaml.safe_load(Path(workflow_path).read_text()),
                    job_name="molecule-setup-ci",
                )

    code_map_list: list[code_block.CodeMap] = code_block.map_reference_to_source(
        tokens=tokens,
        step_to_code_map=step_to_code_map,
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