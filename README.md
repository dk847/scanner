## Setting up the BE/FE environments
```
Terminal 1
#######################################################
cd backend
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# running this separately since it's unsafe to include 'pip-compile' in 'requirements.txt'
pip install pip-tools 

Terminal 2
#######################################################
cd frontend
npm install
```

## Running the script
[Screencast from 2026-03-09 20-12-23.webm](https://github.com/user-attachments/assets/e5e27657-8901-4e61-a309-193209fa1d26)
```
cd backend/app

python3 scanner.py --filepath="../../samples/requirements.txt"
python3 scanner.py --filepath="../../samples/package-lock.json"
python3 scanner.py --filepath="../../samples/package.json"
python3 scanner.py --filepath="../../samples/go.mod"
```
```
CLI arguments
#######################################################
-f, --filepath
Specify the filepath of the manifest you'd like to scan.

-j, --json, --no-json
Include this flag to generate the report in JSON format.
```
```
Example of report in JSON format
#######################################################
{
  "deps_failed_to_scan": ['lodash'],
  "deps_with_vulns": [
    {
      "name": "loader-utils",
      "version": "1.2.3",
      "vulns": [
        {
          "advisory_links": ["https://nvd.nist.gov/vuln/detail/CVE-2022-37603"],
          "aliases": ["CVE-2022-37603"],
          "cve_id": "CVE-2022-37603",
          "fixes": ["1.4.2", "2.0.4", "3.2.1"],
          "severity": "HIGH",
          "summary": "loader-utils is vulnerable to Regular Expression Denial of Service (ReDoS) via url variable"
        }
      ]
    }
  ],
  "scan_count": 2,
  "vuln_count": 1,
  "vuln_percentage": 0.5
}
```

## Running the Flask+React app
[screen-capture.webm](https://github.com/user-attachments/assets/c4999cbf-6fdd-448d-b629-c94df3c73935)
```
Terminal 1
#######################################################
cd backend/app
python3 api.py

Terminal 2
#######################################################
cd frontend
npm run dev
```

## Supported Manifests/Ecosystems
- `requirements.txt` (PyPI)
- `package-lock.json` (npm)
- `package.json` (npm)
- `go.mod` (Go)

## Requirements
1) **Must be written in JavaScript/TypeScript or Python**
   - I've written the script in `Python`.
2) **Must include transitive dependency resolution.**
   - The `requirements.txt` scanner uses the `pip-compile` library to generate a new `generated/requirements.txt` file which includes all dependencies. After, the new file is scanned for any vulnerabilities.
   - The `package.json` scanner only accounts for dependencies defined in the file. For a more thorough analysis, please scan the `package-lock.json` file instead, which includes transitive dependencies.
   - The `go.mod` scanner resolves all dependencies since `go.mod` files include transitive dependencies.
3) **Must use at least one external open source package**
   - Some external Python packages I used are `requests` (used for making API calls) and `result` (used for error handling).
4) **Accepts input via command line (e.g. ./scanner.py requirements.txt)**
   - The CLI accepts 2 arguments (`filepath`, `json`)
5) **Outputs results in both `Huma-readable` and `JSON` format:**
   - Excluding the `--json` flag outputs the report in text format.
   - Including the `--json` flag outputs the report in JSON format.

## Bonus Requirements
1) **Support for multiple ecosystem formats (e.g. in addition to JS & Python other languages).**
   - I added support for the `Go` ecosystem. I also structured the code in a way where you can easily modify `parsers.py` to account for additional ecosystems.
2) **Ability to suppress specific advisories (via an ignore list).**
   - I added an `ADVISARIES_TO_IGNORE` variable to `config.py`, which can be used
   to supress certain vulnerabilities by alias (ex: `CVE-2025-57833`, `GHSA-8ghj-p4vj-mr35`)
3) **Flagging of unmaintained packages (e.g. no releases in past X months).**
   - I didn't add functionality for this; however, I added a `LAST_RELEASE_IN_MONTHS` variable to `config.py` that would account for this.
   - Also, it looks like Github's API has an endpoint for determing the last release; however, it would result in  an additional API call per dependency. I don't think this would be too slow, but perhaps there's an alternate solution.
   - Here's the endpoint I'm referring to: https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-the-latest-release
4) **Optional simple web UI (e.g. Flask or React).**
   - I designed a Flask/React app.

## Notes
* The parser for `package.json` skips dependencies that have versions with `~` or `^`. For a more thorough analysis, please scan the corresponding `package-lock.json` file instead, which includes exact versions and transitive dependencies.
- I decided to use the OSV.dev API since I thought it was more accessible than Github's. The downside is that it aggregates data from external sources, which can potentially result in inaccurate records.
- I didn't account for pagination while querying the OSV.dev API for vulnerabilities; however, I would account for it if this was built for a production environment. Pagination is applied when a queryset contains over 1,000 vulnerabilities.
   - Here's documentaion in regards to this: https://google.github.io/osv.dev/post-v1-query/#pagination
- There's a `backend/app/tests` directory which has placeholder files for where I'd write automated tests. I wrote some placeholder test suites which shows certain edge cases I would cover. Usually, I'd write unit tests for all functions, a success/error e2e test for each main function and integration tests for key parts of the codebase.
