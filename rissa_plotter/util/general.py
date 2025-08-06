import numpy as np
import pandas as pd
from typing import List


def expanded_daterange(start: pd.Timestamp, end: pd.Timestamp, freq: str = "SME"):
    """
    Generate a pandas date range expanded by 10 days before the start and after the end date.

    Parameters
    ----------
    start : pd.Timestamp
        The start date of the range.
    end : pd.Timestamp
        The end date of the range.
    freq : str, optional
        Frequency string for the date range (default is "SME").

    Returns
    -------
    pd.DatetimeIndex
        Sequence of dates from (start - 10 days) to (end + 10 days) at the specified frequency.
    """
    start = start - pd.Timedelta(days=10)
    end = end + pd.Timedelta(days=10)
    return pd.date_range(start, end, freq=freq)


def assign_to_nearest(
    timestamps: pd.date_range,
    fixed_dates: pd.date_range,
):
    """
    Assign each timestamp to the nearest fixed date using vectorized operations.
    Parameters
    ----------
    timestamps : pd.DatetimeIndex or pd.Series or pd.date_range
        Sequence of timestamps to be assigned to the nearest fixed date.
    fixed_dates : pd.DatetimeIndex or pd.Series or pd.date_range
        Sequence of fixed dates to which each timestamp will be assigned.
    Returns
    -------
    pd.Series
        Series indexed by the original timestamps, with values being the nearest fixed date for each timestamp.
    """
    timestamps = timestamps.to_numpy()
    fixed_dates = fixed_dates.to_numpy()

    diffs = np.abs(timestamps[:, None] - fixed_dates[None, :])
    nearest_indices = diffs.argmin(axis=1)

    return pd.Series(fixed_dates[nearest_indices], index=timestamps)


def resample(
    df: pd.DataFrame,
    by: List[str],
    columns: List[str],
    percentile: float,
):
    """
    Resamples a DataFrame by grouping on specified columns and computing the given percentile for selected columns.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to be resampled.
    by : list
        List of column names to group by.
    columns : list
        List of column names for which to compute the percentile.
    percentile : float
        The percentile to compute for the specified columns (between 0 and 1).

    Returns
    -------
    pd.DataFrame
        A DataFrame with the computed percentile values for the specified columns, indexed by the group-by columns.

    """
    if 0.0 <= percentile <= 1.0:
        df[columns] = df[columns].astype(float)
        grouped = df.groupby(by)
        resampled = grouped[columns].quantile(percentile, interpolation="linear")
        return resampled.reset_index()
    else:
        raise ValueError("Percentile should be strictly between 0.0 and 1.0")
