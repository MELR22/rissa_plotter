from collections import Counter


def _count_nests(ledges: dict, include_aon: bool = True) -> int:
    """
    Parameters
    ----------
    ledges : dict
        A dictionary containing ledge statuses.
    include_aon : bool, optional
        If True, includes "Apparently occupied nest" in the count (default is True).
    Returns
    -------
    int
        Total number of nests counted.
    Optionally includes "Apparently occupied nest" if `include_aon` is True.
    """
    counts = Counter(ledges.values())

    nests = (
        counts.get("1 chick visible", 0)
        + counts.get("2 chicks visible", 0)
        + counts.get("3 chicks visible", 0)
    )

    if include_aon:
        nests += counts.get("Apparently occupied nest", 0)

    return nests


def _count_chicks(ledges: dict) -> tuple[int, int, int]:
    """
    Parameters
    ----------
    ledges : dict
        A dictionary containing ledge statuses.
    Returns
    -------
    tuple
        Counts of (1 chick, 2 chicks, 3 chicks).
    """
    counts = Counter(ledges.values())

    one_chick = counts.get("1 chick visible", 0)
    two_chicks = counts.get("2 chicks visible", 0)
    three_chicks = counts.get("3 chicks visible", 0)

    return one_chick, two_chicks, three_chicks
