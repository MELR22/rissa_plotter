from collections import Counter

import pandas as pd

from .validators import ValidNumber


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


class HotelData:
    month = ValidNumber(4, 9)

    def __init__(
        self,
        hotels: str | list,
        years: int | list,
        data: pd.DataFrame,
        include_aon: bool = True,
    ):
        self.hotels = hotels
        self.years = years
        self.data = data
        self.include_aon = include_aon

        self._preprocess()
        self._compute_daily_submissions()

    def _preprocess(self):
        self.data["nestCount"] = self.data["ledgeStatuses"].apply(
            lambda x: _count_nests(x, include_aon=self.include_aon)
        )
        chick_counts = self.data["ledgeStatuses"].apply(_count_chicks).apply(pd.Series)
        chick_counts.columns = ["one_chick", "two_chicks", "three_chicks"]
        self.data[["one_chick", "two_chicks", "three_chicks"]] = chick_counts

    def _compute_daily_submissions(self):
        submissions = pd.DataFrame(index=self.data.index)
        submissions["year"] = submissions.index.year
        submissions["date"] = submissions.index.date
        submissions["entry"] = 1

        daily_counts = (
            submissions.groupby(["date", "year"])["entry"].sum().reset_index()
        )
        daily_counts["date"] = pd.to_datetime(daily_counts["date"])
        self.daily_submissions = daily_counts.set_index("date")

    def select_on(self, hotel: str, month: int = None):
        mask = self.data.hotel == hotel
        if month is not None:
            self.month = month
            mask &= self.data.index.month == self.month

        columns = ["one_chick", "two_chicks", "three_chicks"]
        selection = self.data[mask]
        groups = selection.groupby(selection.index.year)
        result = groups.apply(lambda df: df.loc[df["nestCount"].idxmax(), columns])
        return result
