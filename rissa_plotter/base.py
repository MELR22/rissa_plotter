from typing import Optional

import numpy as np
import pandas as pd
import xarray as xr

from rissa_plotter import util


class KittiwalkersData:
    dimension_name = "entity"  # Override in subclass

    def __init__(self, data: pd.DataFrame, submissions: pd.DataFrame):
        self.data = data.copy()
        self.submissions = submissions.copy()
        self._entities = np.unique(self.submissions[self.dimension_name])
        self._years = np.unique(self.submissions["timestamp"].dt.year)

    def __repr__(self):
        return f"<{self.__class__.__name__} with {len(self.entities)} {self.dimension_name}s covering {self.years}>"

    @property
    def entities(self):
        return self._entities

    @property
    def years(self):
        return self._years

    def _to_xarray(
        self,
        parameter: str,
        frequency: str,
        percentile: float,
    ) -> xr.DataArray:
        """
        Converts the internal resampled DataFrame to an xarray.DataArray for the specified parameter. Resampling of the data is based on the given frequency and daterange of the existing date. Per  and computes the specified percentile.

        Parameters
        ----------
        parameter : str
            The name of the parameter/column to extract from the DataFrame.
        frequency : str
            The frequency string (e.g., 'D' for daily, 'SME' for semimonthly) used to resample the data.
        percentile : float
            The percentile value to compute during resampling.
        Returns
        -------
        xr.DataArray
            A DataArray indexed by timestamp and the object's dimension, containing the resampled parameter values.

        """
        df = self.data.copy()
        dim = self.dimension_name

        fixed_dates = util.expanded_daterange(
            df["timestamp"].min(),
            df["timestamp"].max(),
            frequency,
        )
        df["timestamp"] = util.assign_to_nearest(df["timestamp"], fixed_dates).values

        resampled = util.resample(
            df,
            by=["timestamp", dim],
            columns=[parameter],
            percentile=percentile,
        )
        pivoted = resampled.pivot(index="timestamp", columns=dim, values=parameter)
        da = xr.DataArray(pivoted).sortby("timestamp").astype(float)
        da = da.reindex(timestamp=fixed_dates)
        return da

    def total(
        self,
        var: str,
        frequency: str,
        percentile: float,
        entity: Optional[str] | Optional[list[str]] = None,
        year: Optional[int] = None,
    ) -> xr.DataArray:
        """
        Calculates the total of a specified variable over a given dimension, with optional filtering by entity and year.
        Parameters
        ----------
        var : str
            The name of the variable to aggregate.
        frequency : str
            The frequency at which the data is aggregated (e.g., 'daily', 'monthly').
        percentile : float
            The percentile to use when selecting the data.
        entity : Optional[str] | Optional[list[str]], default=None
            The specific entity to filter by. If None, aggregates over all entities.
        year : Optional[int], default=None
            The specific year to filter by. If None, includes all years.
        Returns
        -------
        xr.DataArray
            The aggregated data array, filtered and summed according to the specified parameters.

        """
        data_var = self._to_xarray(var, frequency, percentile)
        dimension = self.dimension_name

        if entity is None:
            selection = data_var.sum(dim=dimension)
        else:
            selection = data_var.sel({dimension: entity}).sum(dim=dimension)
        selection = selection.where(selection != 0)

        if year is not None:
            selection = selection.where(
                selection["timestamp"].dt.year == year, drop=True
            )
        return selection

    def yearly_submissions(self) -> pd.DataFrame:
        df = self.submissions.copy()
        df["year"] = df["timestamp"].dt.year
        dim = self.dimension_name
        df[dim] = pd.Categorical(df[dim], categories=self.entities, ordered=True)
        yearly_counts = df.groupby(["year", dim]).size()
        return yearly_counts.reset_index(name="count")

    def daily_submissions(self) -> pd.DataFrame:
        df = self.submissions.copy()
        df["year"] = df["timestamp"].dt.year
        df["timestamp"] = df["timestamp"].dt.floor("D")
        df["count"] = 1
        df["count"] = df.groupby(["year"])["count"].cumsum()
        return df[["timestamp", "year", "count"]]

    def submissions_per_bin(self, frequency: str, date: str) -> pd.DataFrame:
        """
        Returns the number of submissions per entity for a given date and frequency bin.

        Parameters
        ----------
        frequency : str
            The frequency string (e.g., 'D', 'SME') used to bin the timestamps.
        date : str
            The target date as a string in the format "%d-%m-%Y".

        Returns
        -------
        pd.DataFrame
            DataFrame indexed by station with a 'count' column for submissions in the specified bin.

        """
        df = self.submissions.copy()
        dim = self.dimension_name

        # Generate fixed bins and assign each timestamp to the nearest bin
        fixed_dates = util.expanded_daterange(
            df["timestamp"].min(),
            df["timestamp"].max(),
            frequency,
        )
        df["binned_timestamp"] = util.assign_to_nearest(
            df["timestamp"], fixed_dates
        ).values

        # Parse the date string and match only the date part of the bin
        target_date = pd.to_datetime(date, format="%d-%m-%Y").date()
        mask = df["binned_timestamp"].dt.date == target_date

        # Count submissions per entity (station/hotel/etc.) for the selected bin
        counts = (
            df[mask]
            .groupby(dim)
            .size()
            .reindex(self.entities, fill_value=0)
            .rename("count")
            .reset_index()
        )

        return counts.set_index(dim)


class CityData(KittiwalkersData):
    """
    Handles city-level station data with adult and AON counts,
    supporting resampling and aggregation of submission data.

    Attributes
    ----------
    data : xr.Dataset
        xarray Dataset with dimensions 'timestamp' and 'station', containing 'adultCount' and 'aonCount'.
    submissions : pd.DataFrame
        Original raw submission data with at least 'timestamp' and 'station' columns.
    """

    dimension_name = "station"

    @classmethod
    def from_dataframe(cls, df):
        """
        Create a CityData instance from a DataFrame as downloaded from the Firebase database.
        """
        submissions = df[["timestamp", "station"]].copy()

        columns = ["timestamp", "station", "adultCount", "aonCount"]
        data = df[columns].copy()
        return cls(data=data, submissions=submissions)

    def total_adults(
        self,
        station: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ) -> xr.DataArray:
        """
        Calculate the total number of adult kittiwakes for a given station, year, and percentile.

        Parameters
        ----------
        station : Optional[str], default=None
            The station to filter by. If None, aggregates over all stations.
        year : Optional[int], default=None
            The year to filter by. If None, includes all years.
        percentile : float, default=0.75
            The percentile which used to resample the data.
        frequency : str, default="SME"
            The frequency at which the data is aggregated (e.g., 'daily', 'monthly')
        """
        return self.total(
            "adultCount",
            entity=station,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )

    def total_aons(
        self,
        station: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ) -> xr.DataArray:
        """
        Calculate the total number of apparently occupied nests (AONs) for a given station, year, and percentile.

        Parameters
        ----------
        station : Optional[str], default=None
            The station to filter by. If None, aggregates over all stations.
        year : Optional[int], default=None
            The year to filter by. If None, includes all years.
        percentile : float, default=0.75
            The percentile which used to resample the data.
        frequency : str, default="SME"
            The frequency at which the data is aggregated (e.g., 'daily', 'monthly')

        """
        return self.total(
            "aonCount",
            entity=station,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )


class HotelData(KittiwalkersData):
    dimension_name = "hotel"

    @classmethod
    def from_dataframe(cls, df):
        """
        Create a HotelData instance from a DataFrame as downloaded from the Firebase database.
        """
        data = df.copy()
        submissions = df[["timestamp", "hotel"]].copy()

        return cls(data=data, submissions=submissions)

    def total_adults(
        self,
        hotel: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ):
        return self.total(
            "adultCount",
            entity=hotel,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )

    def total_aons(
        self,
        hotel: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ):
        return self.total(
            "aonCount",
            entity=hotel,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )

    def total_nests(
        self,
        hotel: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ):
        return self.total(
            "nestCount",
            entity=hotel,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )

    def total_chicks(
        self,
        hotel: Optional[str] = None,
        year: Optional[int] = None,
        percentile: float = 0.75,
        frequency: str = "SME",
    ):
        return self.total(
            "chickCount",
            entity=hotel,
            year=year,
            percentile=percentile,
            frequency=frequency,
        )

    def chicks_per_nest(
        self,
        hotel: str,
    ) -> pd.DataFrame:

        columns = ["one_chick", "two_chicks", "three_chicks"]

        mask = self.data["hotel"] == hotel
        selection = self.data[mask]
        grouped = selection.groupby(selection["timestamp"].dt.year)

        return grouped.apply(util.max_nestcount, columns=columns)
