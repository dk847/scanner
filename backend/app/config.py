"""
This file contains config values which aren't defined as a
part of the CLI args for the following reasons:

1) 'ADVISARIES_TO_IGNORE' is easier to maintain in a file since it's a list.
2) 'LAST_RELEASE_IN_MONTHS' is unlikely to change.
"""


ADVISARIES_TO_IGNORE = [
    "CVE-2024-21520",  # for djangorestframework@3.13.1
    "CVE-2025-57833",  # for django@4.1.7
]

# This variable isn't used; however, if I addressed the bonus requirement
# for ignoring unmaintained dependencies, I'd define the config value here
LAST_RELEASE_IN_MONTHS = 12
