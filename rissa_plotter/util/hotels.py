from collections import Counter

import pandas as pd


def count_adults(ledges: dict) -> int:
    """
    Parameters
    ----------
    ledges : dict
        A dictionary containing ledge statuses.
    Returns
    -------
    int
        Total number of adults counted. This might be an under estimation as this method does not account for multiple adult birds on one ledge.
    """
    counts = Counter(ledges.values())

    adults = (
        counts.get("1 chick visible", 0)
        + counts.get("2 chicks visible", 0)
        + counts.get("3 chicks visible", 0)
        + counts.get("Apparently occupied nest", 0)
        + counts.get("Bird standing but no nest", 0)
    )

    return adults


def count_nests(ledges: dict, include_aon: bool = True) -> int:
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


def count_chicks(ledges: dict) -> tuple[int, int, int]:
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

    chick_count = 1 * one_chick + 2 * two_chicks + 3 * three_chicks

    return one_chick, two_chicks, three_chicks, chick_count


def max_nestcount(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """
    Selects the row with the maximum nestCount, and in case of a tie,
    returns the row with the highest value in the '3 chicks' column.
    """

    # Find all rows where nestCount is equal to its maximum value
    max_nestcount_mask = df["nestCount"] == df["nestCount"].max()
    selection = df[max_nestcount_mask]

    # From those, select the row with the highest value in '3 chicks'
    idx_3_chicks = selection["three_chicks"].idxmax()

    return df.loc[idx_3_chicks, columns]
