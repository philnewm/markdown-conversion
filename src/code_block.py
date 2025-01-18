import logging
import requests
import yaml

from markdown_it.token import Token
from pathlib import Path
from urllib.parse import urljoin, urlunparse
from typing import NamedTuple
from src import constants


log = logging.Logger(__file__)


class CodeMap(NamedTuple):
    reference: str
    source_code: str


class CodeReferenceMeta(NamedTuple):
    file_path: Path
    title: str
    language: str
    source: str
    markup: str



def map_step_name_to_code(
    gh_workflow: dict[str, dict[str, str]]
) -> dict[str, str]:
    """Convert a Github Actions job dictionary to a step to code dictionary.

    Converts a GitHub Actions job steps to a {step-name: run-code} dictionary.

    Args:
        gh_workflow (dict[str, dict]): Dictionary of Yaml content of a Github Actions workflow

    Returns:
        dict[str, str]: Step-name as key and Step run-code as value
    """

    if "jobs" not in gh_workflow:
        raise ValueError("Couldn't find jobs in the workflow file")
    
    if len(gh_workflow["jobs"]) > 1:
        raise ValueError("Multiple jobs in the workflow file")

    yaml_content: dict[str, dict[str, str]] = gh_workflow
    first_key: str = next(iter(yaml_content["jobs"].keys()))
    steps: dict[str, str] = gh_workflow["jobs"][first_key]["steps"]

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
        source=(
                f"{token.markup}{token.info}\n{token.content}{token.markup}"
            ),
        markup=token.markup,
    )


def download_file_from(domain: str, source: str, output_file: Path = Path("local_tmp")) -> Path:

    # TODO research how to download all files at once

    url_prefix: str = urlunparse(("https", domain, "", "", "", ""))
    source_file: str = urljoin(f"{url_prefix}/", source.lstrip("/"))

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        response: requests.Response = requests.get(source_file)
        response.raise_for_status()

        with open(str(output_file), "w", encoding="utf-8") as file:
            file.write(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the download: {e}")\

    except OSError as e:
        print(f"An error occurred with the file system: {e}")

    return output_file


def format_source_code(ref_meta: CodeReferenceMeta, source_code: str) -> str:
    return f"```{ref_meta.language}\n{source_code}```"


def get_code_refs(tokens: list[Token]) -> list[CodeReferenceMeta]:

    ref_list: list[CodeReferenceMeta] = []

    for token in tokens:
        if token.type == constants.code_block and token.info == constants.code_info:

            ref_meta: CodeReferenceMeta = get_reference_values(token=token)
            ref_list.append(ref_meta)

    return ref_list


def get_workflow_code(files: list[Path], path: Path) -> dict[str, str]:

    combined_maps: dict[str, str] = {}

    for file in files:
        step_to_code_map: dict[str, str] = map_step_name_to_code(
            gh_workflow=yaml.safe_load(Path(path / file).read_text())
        )

        combined_maps.update(step_to_code_map)

    return combined_maps

def map_reference_to_source(code_refs: list[CodeReferenceMeta], path: Path, step_to_code_maps: dict[str, str]) -> list[CodeMap]:
    """Map the code references to the source code they point to.

    Args:
        code_refs (list[CodeReferenceMeta])): Code reference found in the markdown file
        step_to_code_maps (dict[str, str]): Workflow step name to code mapping

    Returns:
        list[CodeMap]: List of code mappings
    """

    code_map_list: list[CodeMap] = []

    # ToDo Implement blog dataclass to hold information like title, tags and so on

    for code_ref in code_refs:
        output_file: Path = path / code_ref.file_path

        if code_ref.file_path.parent.name == constants.workflow_directory:
            source_code: str = step_to_code_maps[code_ref.title]
            source_code_formatted: str = f"```{code_ref.language}\n{source_code}```"
            code_map_list.append(
                CodeMap(
                reference=code_ref.source,
                source_code=source_code_formatted,
                )
            )
            continue

        source_code = output_file.read_text()
        source_code_formatted = f"```{code_ref.language}\n{source_code}```"

        code_map_list.append(
            CodeMap(reference=code_ref.source, source_code=source_code_formatted)
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
