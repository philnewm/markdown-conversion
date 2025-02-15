#!/bin/bash

rm -Rf local_tmp
rm -Rf code_output

file_list="https://raw.githubusercontent.com/philnewm/markdown-conversion/refs/heads/main/tests/integrationtests/text.md"

python3.11 markdown_conversion.py download "$file_list"
python3.11 markdown_conversion.py insert-code-references "output_code/"
python3.11 markdown_conversion.py replace-admonitions "output_code/" "output_admonitions/"
