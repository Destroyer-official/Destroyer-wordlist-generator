"""
Main execution module for python -m destroyer
"""

from __future__ import annotations

import sys
from destroyer.cli import main

if __name__ == "__main__":
    sys.exit(main() or 0)
