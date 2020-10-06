import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from .fixtures.workflow import test_workflow
