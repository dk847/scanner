## Setting up the BE/FE environments
```
# Terminal 1
cd backend
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# Terminal 2
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
Include this flag to generate a report in JSON format.
```

## Running the Flask+React app
[screen-capture.webm](https://github.com/user-attachments/assets/8c03d600-e8fb-4a95-aa27-7f2021847555)
```
# Terminal 1
cd backend/app
python3 api.py

# Terminal 2
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
   - The `package.json` scanner only accounts for dependencies defined in the file; however, for a more thorough analysis, please use the `package-lock.json` scanner, which resolves transitive dependencies.
   - The `go.mod` scanner resolves transitive dependencies since `go.mod` files include all dependencies.
3) **Must use at least one external open source package**
   - Some external Python packages I used are `requests` (used for making API calls) and `result` (used for error handling).
4) **Accepts input via command line (e.g. ./scanner.py requirements.txt)**
   - The CLI accepts 2 arguments (`filepath`, `json`)
5) **Outputs results in both `Human-readable` and `JSON` format:**
   - Excluding the `--json` flag outputs the report in text format.
   - Including the `--json` flag outputs the report in JSON format.

## Bonus Requirements
1) **Support for multiple ecosystem formats (e.g. in addition to JS & Python other languages).**
   - I added support for the `Go` ecosystem. I also structured the code in a way where you can easily modify `parser.py` to account for additional ecosystems.
2) **Ability to suppress specific advisories (via an ignore list).**
   - I added a `ADVISARIES_TO_IGNORE` variable to `constants.py`, which can be used
   to flag certain vulnerabilities by alias (ex: `CVE-2025-57833`, `GHSA-8ghj-p4vj-mr35`)
3) **Flagging of unmaintained packages (e.g. no releases in past X months).**
   - I didn't add functionality for this; however, I added a `LAST_RELEASE_IN_MONTHS` variable to `config.py` that would account for this.
   - Also, it looks like the GitHub Securities Advisories API has an endpoint for determing the last release; however, it would result in  an additional API call per dependency. I don't think this would be too slow, but perhaps there's an alternate solution.
   - Here's the endpoint I'm referring to:
      - https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-the-latest-release
4) **Optional simple web UI (e.g. Flask or React).**
   - I designed a Flask/React app.

## Notes
* The parser for `package.json` skips dependencies that have versions with `~` or `^`. For a more thorough analysis, please scan the corresponding `package-lock.json` file instead, which includes exact versions.
- I decided to use the OSV.dev API since I thought it was more accessible than GHSA's. The downside is that it aggregates data from external sources, which can potentially result in inaccurate records.
- I didn't account for pagination while querying the OSV.dev API for vulnerabilities; however, I would account for it if this was built for a production environment.
   - Here is documentaion in regards to the API's pagination:
   - https://google.github.io/osv.dev/post-v1-query/#pagination
- There's a `backend/app/tests` directory which has placeholder files for where I'd write automated tests. I wrote some placeholder test suites which shows certain edge cases I would test. Usually, I'd write tests for all functions in the codebase.
