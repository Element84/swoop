#!/usr/bin/env python
import sys
from pathlib import Path

import yaml

from swoop.api.app import get_app

OUTPUT = Path(__file__).parent.parent.joinpath("openapi.yaml")


if __name__ == "__main__":
    current = OUTPUT.read_text()
    new = yaml.safe_dump(get_app().openapi())

    if current != new:
        OUTPUT.write_text(new)
        sys.exit(1)
