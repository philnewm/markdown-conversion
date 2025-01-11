import pytest

from src.lib import admonition


@pytest.fixture
def admonitions_obsidian() -> str:
    return "> [!tip] Something\n> [!info] More Things\n> [!info] More Things\n> [!warning] Nothing"

@pytest.fixture
def admonitions_devto() -> str:
    return "> **🟢 Tip** - Something\n> **ℹ️ Info** - More Things\n> **ℹ️ Info** - More Things\n> **⚠️ Warning** - Nothing"

@pytest.fixture
def admonitions_medium() -> str:
    return "> **🟢 Tip** - Something\n> **ℹ️ Info** - More Things\n> **ℹ️ Info** - More Things\n> **⚠️ Warning** - Nothing"


def test_admonition_recognition(
    admonitions_obsidian: str, admonitions_devto: str
) -> None:
    """
    Given a admonition examples from obsidian to dev.to
    When utilizing an admonition dataclass
    Than replace as expected
    """

    expected_result: str = admonitions_devto
    result: str = admonitions_obsidian

    for admonition_instance in admonition.admonitions:
        result: str = result.replace(admonition_instance.obsidian, admonition_instance.devto)

    assert expected_result == result


def test_format_admonitions_for_medium(
    admonitions_obsidian: str, admonitions_medium: str
) -> None:

    expected_result: str = admonitions_medium
    result: str = admonitions_obsidian

    for admonition_instance in admonition.admonitions:
        result: str = result.replace(admonition_instance.obsidian, admonition_instance.medium)

    assert expected_result == result


def test_format_admonitions_for_medium(
    admonitions_obsidian: str, admonitions_medium: str
) -> None:

    expected_result: str = admonitions_medium
    result: str = admonitions_obsidian

    for admonition_instance in admonition.admonitions:
        result: str = result.replace(admonition_instance.obsidian, admonition_instance.medium)

    assert expected_result == result
