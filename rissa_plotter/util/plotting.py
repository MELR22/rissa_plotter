from importlib.resources import files
import matplotlib.image as mpimg
import matplotlib.font_manager as fm

import pandas as pd


class ColorMap:
    cream = "#FFF8EE"
    c1 = "#2A3D45"
    c2 = "#81B080"
    c3 = "grey"
    c4 = "#9BB7C3"
    c5 = "#3F553E"
    c6 = "#fe2300"
    c7 = "#fdf55f"


def get_logo():
    # Get a path-like object to the file inside the package
    logo_path = files("rissa_plotter.visualize.data") / "logo_green.png"
    return mpimg.imread(logo_path)


def get_chelsea_font():
    # Get a path-like object to the file inside the package
    font_path = files("rissa_plotter.visualize.data") / "ChelseaMarket-Regular.ttf"
    fm.fontManager.addfont(font_path)
    return fm.FontProperties(fname=font_path)


def add_month_day_columns(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """
    Add 'month_day', 'year', and 'plot_date' columns to align by calendar day across years.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a datetime index.

    Returns
    -------
    pd.DataFrame
        Modified DataFrame with added columns.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            "DataFrame index must be a DatetimeIndex to add month and day columns."
        )
    if not inplace:
        df = df.copy()
    df["month_day"] = df.index.strftime("%m-%d")
    df["year"] = df.index.year
    df["plot_date"] = pd.to_datetime("2000-" + df["month_day"], format="%Y-%m-%d")
    return df
