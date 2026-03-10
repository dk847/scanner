"""
This file contains functions for making API calls to
OSV.dev and Github Security Advisories
"""

import requests

from result import Err, Ok, Result
from typing import List, Optional


class OsvAPIClient:
    BASE_URL = "https://api.osv.dev/v1"
    CVE_FILTER_KEY = "CVE"
    ADVISORY_FILTER_KEY = "ADVISORY"

    # API calls
    def scan_dep(self, name: str, version: str, ecosystem: str) -> Result[dict, str]:
        """
        Description: Gets a list of vulnerabilities from the API and maps the data to a dictionary.
        Documentation: https://google.github.io/osv.dev/post-v1-query/
        Example:
            curl -d \
            '{"package": {"name": "nokogiri", "ecosystem": "RubyGems"}, "version": "1.18.2"}' \
            "https://api.osv.dev/v1/query"
        """

        resp = requests.post(
            url=f"{self.BASE_URL}/query",
            json={
                "version": version,
                "package": {"name": name, "ecosystem": ecosystem},
            },
        )
        if resp.status_code != 200:
            return Err(resp.text)

        parsed_vulns = self.parse_vulns(
            name=name,
            version=version,
            ecosystem=ecosystem,
            vulns=resp.json().get("vulns", []),
        )
        return Ok(parsed_vulns)

    # Helper functions for parsing response data
    def parse_vulns(
        self,
        name: str,
        version: str,
        ecosystem: str,
        vulns: List[dict],
    ) -> dict:
        vuln_dicts = []
        for vuln in vulns:
            result = self.parse_vuln(vuln=vuln)
            vuln_dicts.append(result)

        return {
            "name": name,
            "version": version,
            "ecosystem": ecosystem,
            "vulns": vuln_dicts,
        }

    def parse_vuln(self, vuln: dict) -> dict:
        summary = vuln.get("summary")
        database_specific = vuln.get("database_specific")
        aliases = vuln.get("aliases", [])
        refs = vuln.get("references", [])
        affected = vuln.get("affected", [])

        cve_id = self.find_cve_id(aliases=aliases)
        severity = self.find_severity(database_specific=database_specific)
        advisory_links = self.find_advisory_links(refs=refs)
        fixes = self.find_fixes(affected=affected)

        return {
            "severity": severity,
            "cve_id": cve_id,
            "aliases": aliases,
            "summary": summary,
            "advisory_links": advisory_links,
            "fixes": fixes,
        }

    def find_cve_id(self, aliases: List[str]) -> Optional[str]:
        """
        Example of 'aliases':

        [
            "CVE-2019-10906",
            "PYSEC-2019-217"
        ]
        """

        cve_id = None

        filtered_aliases = list(
            filter(lambda alias: self.CVE_FILTER_KEY in alias, aliases)
        )
        if len(filtered_aliases) > 0:
            cve_id = filtered_aliases[0]

        return cve_id

    def find_severity(self, database_specific: Optional[dict]) -> Optional[str]:
        """
        Example of 'database_specific':

        {
            "github_reviewed_at": "2024-05-06T14:20:59Z",
            "cwe_ids": [
                "CWE-79"
            ],
            "nvd_published_at": "2024-05-06T15:15:23Z",
            "github_reviewed": true,
            "severity": "MODERATE"
        }
        """

        if database_specific:
            return database_specific.get("severity")

        return None

    def find_advisory_links(self, refs: List[str]) -> Optional[str]:
        """
        Example of 'refs':

        [
            {
                "type": "ADVISORY",
                "url": "https://nvd.nist.gov/vuln/detail/CVE-2019-10906"
            },
            {
                "type": "WEB",
                "url": "https://usn.ubuntu.com/4011-2"
            },
        ]
        """

        urls = []

        filtered_refs = list(
            filter(lambda ref: ref["type"] == self.ADVISORY_FILTER_KEY, refs)
        )
        for ref in filtered_refs:
            url = ref["url"]
            urls.append(url)

        return urls

    def find_fixes(self, affected: List[dict]) -> List[str]:
        """
        Example of 'affected':

        [
            {
                "package": {
                    "name": "jinja2",
                    "ecosystem": "PyPI",
                    "purl": "pkg:pypi/jinja2"
                },
                "ranges": [
                    {
                        "type": "ECOSYSTEM",
                        "events": [
                            {"introduced": "0"},
                            {"fixed": "2.10.1"}
                        ]
                    }
                ],
                "versions": ["2.0", "2.0rc1"],
                "database_specific": {"source": https://example-ghsa-link.com}
            }
        ]
        """

        fixes = []
        for aff in affected:
            for range in aff["ranges"]:
                for event in range["events"]:
                    fix = event.get("fixed")
                    if fix:
                        fixes.append(fix)

        return fixes


class GsaAPIClient:
    def scan_dep(self, name: str, version: str, ecosystem: str) -> Result[dict, str]:
        """
        I didn't write logic for the Github Security Advisories API,
        but I would have this function match the shape and naming
        convention of 'OsvAPIClient.scan_dep()' if I did. This way,
        you can replace one API call with the other without changing
        any logic in the business layer.
        """

        pass
