#!/bin/bash

rm -Rf local_tmp
rm -Rf code_output

file_list="https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/README.md, https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/TODO.md, https://raw.githubusercontent.com/philnewm/blog-articles/refs/heads/draft/ansible/molecule_getting_started/ansible_molecule_using_vagrant_and_virtualbox.md"

python3.11 markdown_conversion.py download "$file_list"
python3.11 markdown_conversion.py insert-code-references "/home/dev_test/Documents/output_code"
