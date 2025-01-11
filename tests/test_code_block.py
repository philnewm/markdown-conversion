from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

from src import code_block


@pytest.fixture
def test_workflow() -> dict[str, dict[str, dict[str, list[dict[str, str]]]]]:
    return {
        "jobs": {
            "test_job": {
                "steps": [
                    {"name": "First Task", "run": "echo 'First Task'"},
                    {"name": "Second Task", "run": "echo 'Second Task'"},
                    {"name": "Third Task", "run": "echo 'Third Task'"},
                ]
            },
        }
    }


@pytest.fixture
def code_ref_meta_workflow(tmp_path: Path) -> code_block.CodeReferenceMeta:
    workflow_file: str = "test_workflow.yml"
    code_reference: Path = tmp_path / workflow_file
    return code_block.CodeReferenceMeta(
        file_path=code_reference, title="First Task", language="bash"
    )


def test_map_step_name_to_code(test_workflow: dict[str, dict[str, str]]) -> None:
    """
    Given a test dictionary resembling a github workflow script.
    When running the map conversion
    Than provide the expected dictionary
    """

    expected_result: dict[str, str] = {
        "First Task": "echo 'First Task'",
        "Second Task": "echo 'Second Task'",
        "Third Task": "echo 'Third Task'",
    }

    result: dict[str, str] = code_block.map_step_name_to_code(
        gh_workflow=test_workflow, job_name="test_job"
    )

    assert isinstance(result, dict)
    assert expected_result == result


def test_parse_workflow_code(
    code_ref_meta_workflow: code_block.CodeReferenceMeta,
    test_workflow: dict[str, dict[str, dict[str, list[dict[str, str]]]]],
) -> None:
    """
    Given code reference meta data and test workflow data
    When running parse_workflow_code
    Than provide the queried code as a string
    """

    step_to_code_map: dict[str, str] = code_block.map_step_name_to_code(
        gh_workflow=test_workflow,
        job_name="test_job",
    )

    expected_result = "echo 'First Task'"
    result_key: str = code_block.parse_workflow_code(
        reference_meta=code_ref_meta_workflow,
        jobs=step_to_code_map.keys(),
    )
    result: str = step_to_code_map[result_key]

    assert isinstance(result, str)
    assert expected_result == result


# TODO move non-test related code out of here
class TestToken(NamedTuple):
    __test__ = False
    content: str


@pytest.fixture
def test_token() -> TestToken:
    test_token = TestToken(content="'file': 'path/to/test/file.yml'\ntitle: 'Test Title'\n'language': 'bash'")

    return test_token


def test_get_reference_values(test_token: TestToken) -> None:
    """
    Given a token includign testing data
    When running get_reference_values
    Than expect a CodeReferenceMetaData object containing the keys file, title, language 
    """

    expected_result: dict[str, str] = yaml.safe_load(test_token.content)
    result: code_block.CodeReferenceMeta = code_block.get_reference_values(token=test_token)

    assert isinstance(result, code_block.CodeReferenceMeta)
    assert expected_result["file"] == result.file_path.as_posix()
    assert expected_result["title"] == result.title
    assert expected_result["language"] == result.language
