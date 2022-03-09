import warnings
from typing import Optional

import pytz
import typer
from dateutil import parser
from dateutil.relativedelta import relativedelta
from pytz_deprecation_shim import PytzUsageWarning
from tzlocal import get_localzone

from datetime import datetime

US_TIME_FORMAT = "%I:%M%p"

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
def duration(start_time: str = typer.Argument(None, help="TEST",), end_time: str = typer.Argument(None, help="TEST2"),
             start_tz: str = typer.Option(LOCAL_TIMEZONE), end_tz: str = typer.Option(LOCAL_TIMEZONE)):
    _duration(start_time, start_tz, end_time, end_tz)


def _duration(start_time: str, start_tz: str, end_time: str, end_tz: str):
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


@app.command()
def equivalent(base_time: str = typer.Argument(None, help="Time to check in a different timezone",),
               base_tz: str = typer.Option(LOCAL_TIMEZONE, help="Timezone for reference time. Defaults to local time"),
               target_tz: Optional[str] = typer.Option(LOCAL_TIMEZONE, help="Timezone for equivalent time. Defaults to local time")):
    """
    Command to show what the equivalent of one time in a timezone is in another.
    """
    raw_base_datetime = parser.parse(base_time)
    base_tz = _get_timezone(base_tz)
    target_tz = _get_timezone(target_tz)
    base_datetime = base_tz.localize(raw_base_datetime)
    target_datetime = base_datetime.astimezone(target_tz)
    days_offset = _days_offset(base_datetime, target_datetime)
    target_time_formatted = target_datetime.strftime(US_TIME_FORMAT)
    if days_offset >= 1:
        target_time_formatted += f" +{days_offset}D"
    elif days_offset <=-1:
        target_time_formatted += f" {days_offset}D"
    typer.echo(target_time_formatted)


# currently, only supports America/New_York or UTC
# not CDT, New York, NY, Atlanta, etc.
def _get_timezone(input_string):
    try:
        timezone = pytz.timezone(input_string)
    except pytz.UnknownTimeZoneError:
        # TODO: also add new keword --city which will just be hardcoded to related TZ
        raise NotImplementedError("TODO: add US shorthand to timezone mapping")
    return timezone


def _days_offset(datetime1, datetime2):
    """
    Compute the number of days between the first date and the second date.
    :param datetime1:
    :param datetime2:
    :return: 0 if same day, 1 if second date is ahead of first date, -1 if first date ahead of second date
    """
    # If positive, means second date is ahead of first date
    year_offset = datetime2.year - datetime1.year
    # First check if we are spanning a new year
    if year_offset == 0:
        month_offset = datetime2.month - datetime1.month
        # Then check if spanning new month
        if month_offset == 0:
            # If same year and month then simple arithmatic delta of days
            day_offset = datetime2.day - datetime1.day
            day_adjustment = day_offset
        else:
            # If same year but different month know +- 1 day in same direction as month difference
            day_adjustment = month_offset
    else:
        # If different year know  +- 1 day in same direction as year difference
        day_adjustment = year_offset
    return day_adjustment


if __name__ == "__main__":
    app()
