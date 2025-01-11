from src import code_block, admonition, file
from markdown_it import MarkdownIt
from markdown_it.token import Token
from pathlib import Path

import yaml

# TODO implement pre commit hook that enforces an empty line at the end of each file


# TODO make it run from src directory right away - doesn't work for workflow file so far
script_dir: Path = Path(__file__).resolve().parent
root_dir: Path = script_dir.parent

root_dir = script_dir.parent
input_file: Path = root_dir / "ansible-articles/ansible_molecule/getting_started/Ansible Molecule using Vagrant & Virtualbox.md"
workflow_path: Path = root_dir / "ansible-articles/.github/workflows/run_code_snippets.yml"
output_file_devto: Path = root_dir / "ansible-articles/blog/docs/getting_started_devto.md"
output_file_ghpages: Path = root_dir / "ansible-articles/blog/docs/getting_started.md"

step_to_code_map:dict[str, str] = code_block.map_step_name_to_code(
        gh_workflow=yaml.safe_load(Path(workflow_path).read_text()),
        job_name="molecule-setup-ci",
    )

md = MarkdownIt()

md_content: str = file.read_file(str(input_file))
tokens: list[Token] = md.parse(md_content)
code_map_list: list[code_block.CodeMap] = code_block.map_reference_to_source(
    workflow_path=workflow_path,
    tokens=tokens,
    step_to_code_map=step_to_code_map,
    )
export_content: str = code_block.update_text(md_content, code_map_list)

# write updated markdown file
output_file_ghpages.write_text(export_content)

for admonition in admonition.admonitions:
    export_content: str = export_content.replace(admonition.obsidian, admonition.devto)

output_file_devto.write_text(export_content)