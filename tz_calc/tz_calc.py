import warnings
from typing import Optional

import pytz
import typer
from dateutil import parser
from dateutil.relativedelta import relativedelta
from pytz_deprecation_shim import PytzUsageWarning
from tzlocal import get_localzone

DEBUG = False


def _local_timezone(debug=False):
    if debug:
        local_timezone = get_localzone().zone
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=PytzUsageWarning)
            local_timezone = get_localzone().zone
    return local_timezone


LOCAL_TIMEZONE = _local_timezone(DEBUG)

app = typer.Typer()


@app.command()
def duration(start_time: str, end_time: str,
             start_tz: str = typer.Option(LOCAL_TIMEZONE), end_tz: Optional[str] = typer.Option(LOCAL_TIMEZONE)):
    tz_duration(start_time, start_tz, end_time, end_tz)


@app.command()
def equivalent(base_time: str, base_tz: str = typer.Option(LOCAL_TIMEZONE),
               target_tz: Optional[str] = typer.Option(LOCAL_TIMEZONE)):
    raise NotImplementedError("Will show equiavalent time from one tz to the next")
    # tz_duration(base_time, base_tz, target_time, target_tz)


def tz_duration(start_time: str, start_tz: str, end_time: str, end_tz: str):
    raw_start_datetime = parser.parse(start_time)
    raw_end_datetime = parser.parse(end_time)
    start_tz = _get_timezone(start_tz)
    end_tz = _get_timezone(end_tz)
    start_datetime = start_tz.localize(raw_start_datetime)
    end_datetime = end_tz.localize(raw_end_datetime)
    delta = relativedelta(end_datetime, start_datetime)
    response = f"{delta.hours}"
    if abs(delta.hours) == 1:
        response += " hr"
    else:
        response += " hrs"
    typer.echo(response)
    return delta


# currently, only supports America/New_York or UTC
# not CDT, New York, NY, Atlanta, etc.
def _get_timezone(input_string):
    try:
        timezone = pytz.timezone(input_string)
    except pytz.UnknownTimeZoneError:
        raise NotImplementedError("TODO: add city and US shorthand to timezone mapping")
    return timezone


if __name__ == "__main__":
    app()
