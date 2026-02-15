from .templates import DeltaTemplate


def strfdelta(td, fmt):
    """Format a timedelta object using a format string.

    Args:
        td: A timedelta object to format
        fmt: A format string with $D, $H, $M, $S placeholders

    Returns:
        A formatted string with placeholders replaced by timedelta components
    """
    total_seconds = int(td.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return fmt.replace('$D', str(days)).replace('$H', str(hours)).replace('$M', str(minutes)).replace('$S',
                                                                                                      str(seconds))


# def strfdelta(tdelta, fmt):
#     d = {"D": tdelta.days}
#     d["H"], rem = divmod(tdelta.seconds, 3600)
#     d["M"], d["S"] = divmod(rem, 60)
#     t = DeltaTemplate(fmt)
#     return t.substitute(**d)
