"""
This file contains business logic for getting/filtering API data
and formatting it as JSON or text format.
"""

import os

from typing import List, Optional
from werkzeug.datastructures.file_storage import FileStorage

from constants import API_TMP_DIR_NAME
from integrators import OsvAPIClient
from parsers import open_file_and_map_deps


def scan_deps_and_construct_report(
    osv_api: OsvAPIClient,
    deps: List[dict],
    advisories_to_ignore: List[str],
) -> dict:
    """
    Scans dependencies, constructs an overview and returns the data
    in JSON and text format.
    """

    print("Scanning manifest.\n")

    scanned_results = scan_deps(osv_api=osv_api, deps=deps)
    overview = construct_overview(
        scanned_deps=scanned_results["scanned_deps"],
        deps_failed_to_scan=scanned_results["deps_failed_to_scan"],
        advisories_to_ignore=advisories_to_ignore,
    )
    return {"json": overview, "text": format_report_as_text(overview=overview)}


def scan_deps(osv_api: OsvAPIClient, deps: List[dict]) -> dict:
    """
    Scans a dependency by sending it to the OSV.dev API.
    """

    deps_failed_to_scan = []
    scanned_deps = []

    for dep in deps:
        name = dep["name"]
        version = dep["version"]
        ecosystem = dep["ecosystem"]

        print(f"{name}@{version}")

        result = osv_api.scan_dep(
            name=name,
            version=version,
            ecosystem=ecosystem,
        )
        if result.is_err():
            err_msg = result.unwrap_err()
            print(
                "Failed to scan dependency. | "
                f"name={name}, version={version} | ecosystem={ecosystem}, "
                f" error={err_msg}"
            )
            deps_failed_to_scan.append(name)
            continue

        scanned_dep_dict = result.unwrap()
        scanned_deps.append(scanned_dep_dict)

    # Adds a new line after the dependencies are scanned.
    print("")

    return {
        "scanned_deps": scanned_deps,
        "deps_failed_to_scan": deps_failed_to_scan,
    }


def construct_overview(
    scanned_deps: List[dict],
    deps_failed_to_scan: List[str],
    advisories_to_ignore: List[str],
) -> dict:
    """
    Constructs an overview of all scanned dependencies.
    """

    deps_with_vulns = list(filter(lambda dep: len(dep["vulns"]) > 0, scanned_deps))
    filtered_deps_with_vulns = filter_deps_with_vulns(
        deps=deps_with_vulns,
        advisories_to_ignore=advisories_to_ignore,
    )

    scan_count = len(scanned_deps)
    vuln_count = len(filtered_deps_with_vulns)

    vuln_percentage = 0
    if scanned_deps:
        vuln_percentage = round(
            number=float(vuln_count) / float(scan_count),
            ndigits=3,
        )

    return {
        "scan_count": scan_count,
        "vuln_count": vuln_count,
        "vuln_percentage": vuln_percentage,
        "deps_with_vulns": filtered_deps_with_vulns,
        "deps_failed_to_scan": deps_failed_to_scan,
    }


def filter_deps_with_vulns(
    deps: List[dict],
    advisories_to_ignore: List[str],
) -> List[dict]:
    """
    Filters out dependencies that have flagged vulnerabilities.
    """

    filtered_deps = []

    for dep in deps:
        filtered_vulns = []

        for vuln in dep["vulns"]:
            if should_ignore_vuln(
                dep_advisories=vuln["aliases"],
                advisories_to_ignore=advisories_to_ignore,
            ):
                print(
                    f"{dep['name']}: Skipping vulnerability '{vuln['cve_id']}' "
                    "since it's been flagged to skip in 'config.py'."
                )
                continue

            filtered_vulns.append(vuln)

        has_vulns = len(filtered_vulns) > 0
        if has_vulns:
            filtered_deps.append({**dep, "vulns": filtered_vulns})

    return filtered_deps


def should_ignore_vuln(
    dep_advisories: List[str],
    advisories_to_ignore: List[str],
) -> bool:
    """
    Checks if a dependency belongs to the 'ADVISARIES_TO_IGNORE' list.
    """

    for dep_adv in dep_advisories:
        for adv_to_ignore in advisories_to_ignore:
            if dep_adv == adv_to_ignore:
                return True

    return False


def format_report_as_text(overview: dict) -> str:
    """
    Formats the vulnerability report in text format.
    """

    vuln_percentage = round(overview["vuln_percentage"] * 100, 3)
    report = (
        f"Finished scanning manifest. {overview['vuln_count']}/{overview['scan_count']} ({vuln_percentage}%) "
        "successfully scanned dependencies have a vulnerability.\n"
    )

    if overview['deps_failed_to_scan']:
        report += f"Failed to scan the following dependencies: {overview['deps_failed_to_scan']}\n"

    if overview["deps_with_vulns"]:
        report += (
            "\nSummary\n"
            "###############################################"
        )

    for dep in overview["deps_with_vulns"]:
        report += f"\n{dep['name']}@{dep['version']}"

        vulns = dep["vulns"]
        report += f"\n\tVulnerability Count: {len(vulns)}"

        for vuln in vulns:
            report += f"\n\n\tCVE ID: {vuln['cve_id']}"
            report += f"\n\tAliases: {vuln['aliases']}"
            report += f"\n\tSummary: {vuln['summary']}"
            report += f"\n\tSeverity: {vuln['severity']}"
            report += f"\n\tAdvisory Links: {vuln['advisory_links']}"
            report += f"\n\tFixes: {vuln['fixes']}"

        report += "\n"

    return report


def handle_flask_api_call(file: FileStorage, advisories_to_ignore: List[str]) -> dict:
    """
    Handles the Flask API call for the React web app. This function contains
    similar logic to the 'main' function in 'scanner.py'.
    """

    # Uploading file to temp directory so that the parser can process it
    os.makedirs(name=API_TMP_DIR_NAME, exist_ok=True)
    filepath = os.path.join(API_TMP_DIR_NAME, file.filename)
    file.save(filepath)

    deps = open_file_and_map_deps(filepath=filepath)

    osv_api = OsvAPIClient()
    report = scan_deps_and_construct_report(
        osv_api=osv_api,
        deps=deps,
        advisories_to_ignore=advisories_to_ignore,
    )

    return report
