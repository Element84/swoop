"""rfc3339."""

import re
from datetime import datetime
from typing import Optional, Tuple

import iso8601

"""

This module is copied from
https://github.com/stac-utils/stac-fastapi/blob/b9cedf353eae9aaad76c3a9a1e886bfb7c5e04ff/stac_fastapi/types/stac_fastapi/types/rfc3339.py

The license and copyright are as follows:

MIT License

Copyright (c) 2020 Arturo AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


RFC33339_PATTERN = (
    r"^(\d\d\d\d)\-(\d\d)\-(\d\d)(T|t)(\d\d):(\d\d):(\d\d)([.]\d+)?"
    r"(Z|([-+])(\d\d):(\d\d))$"
)


def rfc3339_str_to_datetime(s: str) -> datetime:
    """Convert a string conforming to RFC 3339 to a :class:`datetime.datetime`.

    Uses :meth:`iso8601.parse_date` under the hood.

    Args:
        s (str) : The string to convert to :class:`datetime.datetime`.

    Returns:
        str: The datetime represented by the ISO8601 (RFC 3339) formatted string.

    Raises:
        ValueError: If the string is not a valid RFC 3339 string.
    """
    # Uppercase the string
    s = s.upper()

    # Match against RFC3339 regex.
    result = re.match(RFC33339_PATTERN, s)
    if not result:
        raise ValueError("Invalid RFC3339 datetime.")

    # Parse with pyiso8601
    return iso8601.parse_date(s)


def str_to_interval(
    interval: str,
) -> Optional[Tuple[Optional[datetime], Optional[datetime]]]:
    """Extract a tuple of datetimes from an interval string.

    Interval strings are defined by
    OGC API - Features Part 1 for the datetime query parameter value. These follow the
    form '1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z', and allow either the start
    or end (but not both) to be open-ended with '..' or ''.

    Args:
        interval (str) : The interval string to convert to a :class:`datetime.datetime`
        tuple.

    Raises:
        ValueError: If the string is not a valid interval string.
    """
    if not interval:
        raise ValueError("Empty interval string is invalid.")

    values = interval.split("/")
    if len(values) != 2:
        raise ValueError(
            f"Interval string '{interval}' contains more than one forward slash."
        )

    start = None
    end = None
    if values[0] not in ["..", ""]:
        start = rfc3339_str_to_datetime(values[0])
    if values[1] not in ["..", ""]:
        end = rfc3339_str_to_datetime(values[1])

    if start is None and end is None:
        raise ValueError("Double open-ended intervals are not allowed.")
    if start is not None and end is not None and start > end:
        raise ValueError("Start datetime cannot be before end datetime.")
    else:
        return start, end
