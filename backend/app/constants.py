"""
This file contains constants which are used throughout the codebase.
"""

from enum import Enum


class Manifest(Enum):
    """
    Manifests which this script can support.
    """

    REQUIREMENTS_TXT = "requirements_txt"
    PACKAGE_JSON = "package_json"
    PACKAGE_LOCK_JSON = "package_lock_json"
    GO_MOD = "go_mod"


class Ecosystems(Enum):
    """
    Ecosystems which this manifest can support.

    NOTE: The enum value is formatted to satisfiy the 'ecosystem' parameter
    in the OSV.dev API.
    """

    PYPI = "PyPI"
    NPM = "npm"
    GO = "Go"


MANIFEST_TYPES = [manifest.value for manifest in Manifest]
GENERATED_DIR_NAME = "generated"  # Directory where files from this script are generated
API_TMP_DIR_NAME = "tmp"  # Directory where manifests from the Flask API are uplodaed

# Keywords for determining manifest type from file name
REQUIREMENTS_TXT_KEYWORD = ".txt"
PACKAGE_LOCK_JSON_KEYWORD = "lock.json"
PACKAGE_JSON_KEYWORD = ".json"
GO_MOD_KEYWORD = ".mod"
