"""
This file contains the 'main' function, which runs the script.
"""

import pprint

from argparse import ArgumentParser, BooleanOptionalAction

from business import scan_deps_and_construct_report
from config import ADVISARIES_TO_IGNORE
from integrators import OsvAPIClient
from parsers import open_file_and_map_deps


def main():
    """
    Example of running command:

    python3 scanner.py --filepath="../../samples/requirements.txt" --json
    """

    parser = setup_cli_args()
    args = parser.parse_args()

    filepath: str = args.filepath
    is_json: bool = args.json != None

    deps = open_file_and_map_deps(filepath=filepath)

    osv_api = OsvAPIClient()
    report = scan_deps_and_construct_report(
        osv_api=osv_api,
        deps=deps,
        advisories_to_ignore=ADVISARIES_TO_IGNORE,
    )

    if is_json:
        pprint.pprint(report["json"], indent=2)
    else:
        print(report["text"])


def setup_cli_args() -> ArgumentParser:
    """
    Configures the CLI parser by setting accepted parameters.
    """

    parser = ArgumentParser()
    parser.add_argument(
        "-f",
        "--filepath",
        help="Specify the filepath of the manifest you'd like to scan.",
        required=True,
    )
    parser.add_argument(
        "-j",
        "--json",
        help="Include this flag to generate a report in JSON format.",
        action=BooleanOptionalAction,
    )
    return parser


main()
