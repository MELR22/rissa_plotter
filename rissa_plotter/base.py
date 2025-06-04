import pandas as pd

from rissa_plotter import util


import pandas as pd
from typing import List


class HotelData:
    """
    Class to process and analyze nesting data from hotels over multiple years.
    """

    def __init__(
        self,
        hotels: List[str],
        years: List[int],
        data: pd.DataFrame,
        include_aon: bool = True,
        month: int = 4,
    ):
        self.hotels = hotels
        self.years = years
        self.data = data.copy()
        self.include_aon = include_aon
        self.month = self._validate_month(month)

        self._prepare_data()

    @staticmethod
    def _validate_month(month: int) -> int:
        """Ensure the month is within the valid range [4, 9]."""
        if not (4 <= month <= 9):
            raise ValueError("Month must be between 4 and 9.")
        return month

    def _prepare_data(self):
        """Preprocess and compute relevant columns."""
        self._add_nest_counts()
        self._add_chick_counts()
        self._compute_daily_submissions()

    def _add_nest_counts(self):
        """Add nest count to the data."""
        self.data["nestCount"] = self.data["ledgeStatuses"].apply(
            lambda x: util._count_nests(x, include_aon=self.include_aon)
        )

    def _add_chick_counts(self):
        """Add one/two/three chick count columns to the data."""
        chick_counts = (
            self.data["ledgeStatuses"].apply(util._count_chicks).apply(pd.Series)
        )
        chick_counts.columns = ["one_chick", "two_chicks", "three_chicks"]
        self.data[["one_chick", "two_chicks", "three_chicks"]] = chick_counts

    def _compute_daily_submissions(self):
        """Compute daily submission counts."""
        submissions = pd.DataFrame(index=self.data.index)
        submissions["year"] = submissions.index.year
        submissions["date"] = submissions.index.date
        submissions["entry"] = 1

        daily_counts = (
            submissions.groupby(["date", "year"])["entry"].sum().reset_index()
        )
        daily_counts["date"] = pd.to_datetime(daily_counts["date"])
        self.daily_submissions = daily_counts.set_index("date")

    def select_on(self, hotel: str, month: int = None) -> pd.DataFrame:
        """
        Select data for a specific hotel and optionally a specific month.
        Returns the row with the maximum nest count for each year.
        """
        mask = self.data.hotel == hotel

        if month is not None:
            month = self._validate_month(month)
            mask = mask & (self.data.index.month == month)

        columns = ["one_chick", "two_chicks", "three_chicks"]
        filtered_data = self.data[mask]
        grouped = filtered_data.groupby(filtered_data.index.year)

        return grouped.apply(lambda df: df.loc[df["nestCount"].idxmax(), columns])


class CityData:
    """
    Processes city-wide nesting data across multiple stations and years.
    Provides resampled daily counts and submission statistics.
    """

    def __init__(
        self,
        years: List[int],
        data: pd.DataFrame,
    ):
        self.years = years
        self.data = data.copy()

        self._prepare_data()

    def _prepare_data(self):
        """Run preprocessing steps on the input data."""
        self._resample_data()
        self._compute_daily_submissions()

    def _resample_data(self):
        """
        Resample data to the specified daily frequency by station.
        Aggregates using max for adult and AON counts.
        """
        start = self.data.index[0].date() - pd.Timedelta(days=10)
        end = self.data.index[-1].date() + pd.Timedelta(days=10)
        date_range = pd.date_range(start, end, freq="SME")

        temp = self.data.copy().reset_index()
        temp["assigned_date"] = temp["timestamp"].apply(
            lambda ts: util.assign_to_nearest(ts, date_range)
        )

        resampled = (
            temp.groupby(["station", "assigned_date"])
            .agg({"adultCount": "max", "aonCount": "max"})
            .reset_index()
            .rename(columns={"assigned_date": "timestamp"})
        )

        stations = self.data["station"].unique()
        full_index = pd.MultiIndex.from_product(
            [stations, date_range], names=["station", "timestamp"]
        )

        resampled = (
            resampled.set_index(["station", "timestamp"])
            .reindex(full_index, fill_value=0)
            .reset_index()
        )

        columns = ["station", "adultCount", "aonCount"]

        self.resampled = resampled.set_index("timestamp")[columns]

    def _compute_daily_submissions(self):
        """
        Compute number of data entries submitted per day, grouped by year.
        """
        submissions = pd.DataFrame(index=self.data.index)
        submissions["year"] = submissions.index.year
        submissions["date"] = submissions.index.date
        submissions["entry"] = 1

        daily_counts = (
            submissions.groupby(["date", "year"])["entry"].sum().reset_index()
        )
        daily_counts["date"] = pd.to_datetime(daily_counts["date"])
        self.daily_submissions = daily_counts.set_index("date")
