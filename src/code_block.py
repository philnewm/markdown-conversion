import logging
import os
import requests
import yaml

from markdown_it.token import Token
from pathlib import Path
from src import file
from typing import Any, NamedTuple


log = logging.Logger(__file__)
workflow_paths: list[str] = [
    "run_code_snippets.yml",
]


class CodeMap(NamedTuple):
    reference: str
    source_code: str


class CodeReferenceMeta(NamedTuple):
    file_path: Path
    title: str
    language: str
    source: str


def map_step_name_to_code(
    gh_workflow: dict[str, dict[str, str]], job_name: str
) -> dict[str, str]:
    """Convert a Github Actions job dictionary to a step to code dictionary.

    Converts a GitHub Actions job steps to a {step-name: run-code} dictionary.

    Args:
        gh_workflow (dict[str, dict]): Dictionary of Yaml content of a Github Actions workflow
        job_name (str): Job name to use as source

    Returns:
        dict[str, str]: Step-name as key and Step run-code as value
    """

    steps: dict[str, str] = gh_workflow["jobs"][job_name]["steps"]

    return {step["name"]: step.get("run") for step in steps}


def parse_workflow_code(reference_meta: CodeReferenceMeta, jobs: list[str]) -> str:
    """Get code either from file or workflow.

    Args:
        reference_meta (CodeReferenceMeta): Reference meta object
        jobs (list[str]): List of jobs from the workflow file

    Raises:
        ValueError: In case the step name wasn't found in the workflow.

    Returns:
        str: Step name from workflow
    """

    if reference_meta.title not in jobs:
        raise ValueError(
            f"Couldn't find step name '{reference_meta.title}' in workflow '{reference_meta.file_path}'"
        )

    return reference_meta.title


def get_reference_values(token: Token) -> CodeReferenceMeta:
    """Extract meta values from code reference blocks

    Args:
        token (Token): Markdown token

    Returns:
        CodeReferenceMeta: Code reference object 
    """
    reference_dict: dict[str, str] = yaml.safe_load(token.content)

    return CodeReferenceMeta(
        file_path=Path(reference_dict["file"]),
        title=reference_dict["title"],
        language=reference_dict["language"],
        source = (
                f"{token.markup}{token.info}\n{token.content}{token.markup}"
            ),
    )


def download_file_from(base_url: Path, source: Path, output: Path = Path("local_tmp")) -> Path:

    source_file: Path = base_url / str(source)
    output_file: Path = output / source.name

    try:
        output_file.mkdir(parents=True, exist_ok=True)

        response: requests.Response = requests.get(str(source_file))
        response.raise_for_status()

        with open(str(output), "w", encoding="utf-8") as file:
            file.write(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the download: {e}")\

    except OSError as e:
        print(f"An error occurred with the file system: {e}")

    return output_file


def format_source_code(token, ref_meta, source_code) -> tuple[str, str]:
    source_code_formatted: str = f"```{ref_meta.language}\n{source_code}```"
    code_reference: str = (
                f"{token.markup}{token.info}\n{token.content}{token.markup}"
            )

    return source_code_formatted, code_reference


def get_code_refs(tokens: list[Token]) -> list[CodeReferenceMeta]:

    ref_list: list[CodeReferenceMeta] = []

    for token in tokens:
        if token.type == "fence" and token.info == "reference":

            ref_meta: CodeReferenceMeta = get_reference_values(token=token)
            ref_list.append(ref_meta)

    return ref_list



def map_reference_to_source(
    step_to_code_map: dict[str, str]
) -> list[CodeMap]:
    """Map the code references to the source code they point to.

    Args:
        workflow_path (Path): Path to GitHub Action workflow
        tokens (list[Tokens]): Token list from parsed markdown file

    Returns:
        list[CodeMap]: List of code mappings
    """

    code_map_list: list[CodeMap] = []

    # ToDo Implement blog dataclass to hold information like title, tags and so on

    base_url: Path = Path("https://raw.githubusercontent.com/philnewm/blog-articles/drafts/")

            output_file: Path = download_file_from(
                base_url=base_url,
                source=ref_meta.file_path,
                )
            source_code: str = output_file.read_text()

            # Warning assumes yaml-source files to be GitHub-Workflows
            if ref_meta.file_path.name.endswith(".yml"):
                snippet_name: str = parse_workflow_code(
                    reference_meta=ref_meta,
                    jobs=step_to_code_map.keys()
                )
                source_code = step_to_code_map[snippet_name]

            source_code_formatted, code_reference = format_source_code(token, ref_meta, source_code)

            code_map_list.append(
                CodeMap(reference=code_reference, source_code=source_code_formatted)
            )

    return code_map_list


def update_text(source_text: str, code_map_list: list[CodeMap]) -> str:
    """Replace source text with referenced code.

    Args:
        source_text (str): Code reference
        code_map_list (list[CodeMap]): List of reference to code maps

    Returns:
        str: Updated text output
    """

    export_content: str = source_text
    for CodeMap in code_map_list:
        export_content: str = export_content.replace(
            CodeMap.reference, CodeMap.source_code
        )

    return export_content
