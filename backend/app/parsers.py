"""
This file parses manifest files (ex: requirements.txt) and maps the
dependencies to a list of dictionaries.
"""

import json
import os
import subprocess

from typing import List, Optional

from constants import (
    GENERATED_DIR_NAME,
    GO_MOD_KEYWORD,
    PACKAGE_JSON_KEYWORD,
    PACKAGE_LOCK_JSON_KEYWORD,
    REQUIREMENTS_TXT_KEYWORD,
    Ecosystems,
    Manifest,
)


def open_file_and_map_deps(filepath: str) -> dict:
    """
    Opens the manifest file and maps the content to a dictionary.
    """

    mt = determine_manifest_type(filepath=filepath)
    if not mt:
        return []

    deps = []
    if mt == Manifest.REQUIREMENTS_TXT:
        deps = parse_requirements_file(filepath=filepath)
    elif mt == Manifest.PACKAGE_LOCK_JSON:
        deps = parse_package_lock_json_file(filepath=filepath)
    elif mt == Manifest.PACKAGE_JSON:
        deps = parse_package_json_file(filepath=filepath)
    elif mt == Manifest.GO_MOD:
        deps = parse_go_mod_file(filepath=filepath)

    return deps


def determine_manifest_type(filepath: str) -> Optional[Manifest]:
    """
    Determines the manifest type based off of the filename.

    NOTE: I could add some more checks to this function (such as inspecting the file content)
    to make it more robust,
    """

    filename = filepath.split("/")[-1]

    mt = None
    if REQUIREMENTS_TXT_KEYWORD in filename:
        mt = Manifest.REQUIREMENTS_TXT
    elif PACKAGE_LOCK_JSON_KEYWORD in filename:
        mt = Manifest.PACKAGE_LOCK_JSON
    elif PACKAGE_JSON_KEYWORD in filename:
        mt = Manifest.PACKAGE_JSON
    elif GO_MOD_KEYWORD in filename:
        mt = Manifest.GO_MOD

    return mt


# requirements.txt
def parse_requirements_file(filepath: str) -> List[dict]:
    """
    Parses dependencies from a 'requirements.txt' file.
    """

    new_filepath = generate_new_requirements_file(original_filepath=filepath)

    with open(new_filepath, mode="r") as file:
        deps = []

        for line in file:
            dep_elements = line.split("==")
            if len(dep_elements) == 2:
                name = dep_elements[0]
                version = dep_elements[1].split("\n")[0]

                deps.append(
                    {
                        "name": name,
                        "version": version,
                        "ecosystem": Ecosystems.PYPI.value,
                    }
                )

    return deps


def generate_new_requirements_file(original_filepath: str) -> str:
    """
    Generates a new manifest with transitive dependencies using the
    'pip-compile' library.
    """

    filename = original_filepath.split("/")[-1]
    new_filepath = f"{GENERATED_DIR_NAME}/{filename}"

    print(f"Generating new '{filename}', which includes transitive dependencies.")

    os.makedirs(name=GENERATED_DIR_NAME, exist_ok=True)
    subprocess.run(
        [
            "pip-compile",
            original_filepath,
            "-o",
            new_filepath,
            # These args remove noise from the logs and generate a clean file without comments
            "--no-header",
            "--no-annotate",
            "--strip-extras",
            "-q",
        ]
    )

    print(f"Finished generating new '{filename}'.\n")

    return new_filepath


# package-lock.json
def parse_package_lock_json_file(filepath: str) -> List[dict]:
    """
    Parses dependencies from a 'package-lock.json' file.
    """

    with open(filepath, mode="r") as file:
        data = json.load(file)
        all_deps: dict = data.get("packages", {})
        filtered_deps = filter_package_lock_json_packages(all_deps=all_deps)

        deps = []
        for name in filtered_deps.keys():
            dep = filtered_deps[name]

            name = name.split("node_modules/")[-1]
            version = dep["version"]

            deps.append(
                {
                    "name": name,
                    "version": version,
                    "ecosystem": Ecosystems.NPM.value,
                }
            )

    # Sorts by dependency 'name' in ascending alphabetical order
    sorted_deps = sorted(deps, key=lambda d: d["name"])
    return sorted_deps


def filter_package_lock_json_packages(all_deps: dict) -> dict:
    """
    Filters out packages which are from the corresponding 'package.json'
    file since the rest of 'package-lock.json' includes exact versions of
    all dependencies.
    """

    filtered_deps = {}
    for name in all_deps.keys():
        if name != "":
            filtered_deps[name] = all_deps[name]

    return filtered_deps


# package.json
def parse_package_json_file(filepath: str) -> List[dict]:
    """
    Parses dependencies from a 'package.json' file.
    """

    with open(filepath, mode="r") as file:
        data = json.load(file)
        all_deps: dict = data.get("dependencies", {}) | data.get("devDependencies", {})

        filtered_deps = filter_package_json_packages(all_deps=all_deps)

        deps = []
        for name, version in filtered_deps.items():
            version = version.split("^")[-1]

            deps.append(
                {
                    "name": name,
                    "version": version,
                    "ecosystem": Ecosystems.NPM.value,
                }
            )

    # Sorts by dependency 'name' in ascending alphabetical order
    sorted_deps = sorted(deps, key=lambda d: d["name"])
    return sorted_deps


def filter_package_json_packages(all_deps: dict) -> dict:
    """
    Filters out packages which don't include an exact version.
    """

    filtered_deps = {}
    for name, version in all_deps.items():
        if "^" not in version and "~" not in version:
            filtered_deps[name] = all_deps[name]

    return filtered_deps


# go.mod
def parse_go_mod_file(filepath: str) -> List[dict]:
    """
    Parses dependencies from a 'go.mod' file.
    """

    is_dependency = False

    with open(filepath, mode="r") as file:
        deps = []

        for line in file:
            # Indicates that the current line is the end of the 'require' statement
            # in the 'go.mod' file, which means that a dependency shouldn't be parsed
            if ")" in line:
                is_dependency = False

            if is_dependency:
                package_data = parse_go_mod_package(line=line)
                deps.append(
                    {
                        "name": package_data["name"],
                        "version": package_data["version"],
                        "ecosystem": Ecosystems.GO.value,
                    }
                )

            # Indicates that the next line contains a dependency which should be parsed
            if "require (" in line:
                is_dependency = True

    return deps


def parse_go_mod_package(line: str) -> dict:
    """
    Parses the 'name' and 'version' from a go mod package.
    """

    # This accounts for any comments on a dependency line
    if "//" in line:
        line = "".join(line.split("//")[:-1])

    dep_elements = line.split(" ")

    # This removes unnecessary whitespace from a dependency line
    name = dep_elements[0].replace("\n", "").replace("\t", "")
    version = dep_elements[1].replace("\n", "").replace("\t", "")

    return {"name": name, "version": version}
