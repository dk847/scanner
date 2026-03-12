"""
This file contains config values which aren't defined as a
part of the CLI args for the following reasons:

1) 'ADVISARIES_TO_IGNORE' is easier to maintain in a file since it's a list.
2) 'LAST_RELEASE_IN_MONTHS' is unlikely to change.
"""


ADVISARIES_TO_IGNORE = [
    # For loader-utils
    "CVE-2022-37603",
    "CVE-2022-37601",
    "CVE-2022-37599",
]

# This variable isn't used; however, if I addressed the bonus requirement
# for ignoring unmaintained dependencies, I'd define the config value here
LAST_RELEASE_IN_MONTHS = 12
