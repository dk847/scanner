"""
This file contains constants which are used throughout the codebase.
"""

from enum import Enum


class Ecosystems(Enum):
    """
    Ecosystems which this manifest can support.

    NOTE: The enum value is formatted to satisfiy the 'ecosystem' parameter
    in the OSV.dev API.
    """

    PYPI = "PyPI"
    NPM = "npm"
    GO = "Go"


GENERATED_DIR_NAME = "generated"  # Directory where files from this script are generated
API_TMP_DIR_NAME = "tmp"  # Directory where manifests from the Flask API are uplodaed

# Keywords for determining manifest type from file name
REQUIREMENTS_TXT_KEYWORD = ".txt"
PACKAGE_LOCK_JSON_KEYWORD = "lock.json"
PACKAGE_JSON_KEYWORD = ".json"
GO_MOD_KEYWORD = ".mod"

FE_BASE_URL = "http://localhost:3000"
FLASK_API_PORT = 8000
