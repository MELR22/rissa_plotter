from pathlib import Path
import pandas as pd

from rissa_plotter.readers import FireBase


def _clean_city_data(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["adultCount"] = pd.to_numeric(df["adultCount"])
    df["aonCount"] = pd.to_numeric(df["aonCount"])
    df["groupSize"] = (
        pd.to_numeric(df["groupSize"], errors="coerce").fillna(1).astype(int)
    )
    return df


def open_city_table(path: str | Path) -> pd.DataFrame:
    """
    Read a all City data from the Firestore database.

    Parameters
    ----------
    path : str
        Path to the Firebase service account key file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the data from the city data Firestore collection.
    """

    with FireBase(path) as fb:
        current = _clean_city_data(fb.read_table("submissionsKittiwakesCity"))
        legacy = _clean_city_data(fb.read_table("submissionsKittiwakesCity2324"))

    df = pd.concat([legacy, current], ignore_index=True)
    df = df.sort_values(by=["timestamp", "station"], ascending=[True, True])
    df.reset_index(drop=True, inplace=True)

    columns = [
        "userId",
        "displayName",
        "userEmail",
        "station",
        "timestamp",
        "groupSize",
        "adultCount",
        "aonCount",
        "comment",
    ]
    return df[columns]
