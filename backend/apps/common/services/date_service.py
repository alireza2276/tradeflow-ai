from datetime import date

import jdatetime


def gregorian_to_jalali(value: date) -> str:
    jalali_date = jdatetime.date.fromgregorian(date=value)

    return jalali_date.strftime("%Y/%m/%d")


def format_dual_date(value: date) -> str:
    jalali_date = gregorian_to_jalali(value)

    gregorian_date = value.strftime("%Y/%m/%d")

    return f"{jalali_date} ({gregorian_date})"