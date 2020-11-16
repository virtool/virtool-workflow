"""Script to replace the version number in setup.py with a new version number provided as a command line argument."""
import sys
import re
from pathlib import Path

new_version_number = sys.argv[1]

setup_py = Path(__file__).parent/"setup.py"
setup_py_text = setup_py.read_text()

new_setup_py_text = re.sub('version="(.*)"', f'version="{new_version_number}"', setup_py_text)

setup_py.write_text(new_setup_py_text)

