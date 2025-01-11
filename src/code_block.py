import logging
import yaml

from markdown_it.token import Token
from pathlib import Path
from src.lib import file
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
    )


def map_reference_to_source(
    workflow_path: Path, tokens: list[Token], step_to_code_map: dict[str, str]
) -> list[CodeMap]:
    """Map the code references to the source code they point to.

    Args:
        workflow_path (Path): Path to GitHub Action workflow
        tokens (list[Tokens]): Token list from parsed markdown file

    Returns:
        list[CodeMap]: List of code mappings
    """

    code_map_list: list[CodeMap] = []

    # ToDo Implement blog dataclass to hold information like ttitle, tags and so on

    for token in tokens:
        if token.type == "fence" and token.info == "reference":
            ref_meta: CodeReferenceMeta = get_reference_values(token=token)
            source_code: str = file.read_file(file_path=str(ref_meta.file_path))

            if ref_meta.file_path.name in workflow_paths:
                snippet_name: str = parse_workflow_code(
                    reference_meta=ref_meta,
                    jobs=step_to_code_map.keys()
                )
                source_code = step_to_code_map[snippet_name]

            source_code_formatted: str = f"```{ref_meta.language}\n{source_code}```"
            code_reference: str = (
                f"{token.markup}{token.info}\n{token.content}{token.markup}"
            )

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
