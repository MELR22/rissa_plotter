import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.dates import DateFormatter

from .utils import ColorMap, LineStyle, get_logo, get_chelsea_font
from .utils import add_month_day_columns, resample_city_data

logo = get_logo()
chelsea_font = get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class CityPlotter:
    def __init__(self, city_data: pd.DataFrame):
        """
        Initialize CityPlotter with raw city data and prepare resampled version.
        """
        self.city_data = city_data.set_index("timestamp")
        self.resampled = resample_city_data(self.city_data, frequency="SME")

    def plot_timeseries(self, year: int = None, station: str = None, **kwargs):
        """
        Plot time series of kittiwake counts at city stations.

        Parameters
        ----------
        year : int, optional
            Filter the data by year.
        station : str, optional
            Filter the data by station.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure
        """
        data = self.resampled.copy()
        title = "Kittiwakes at City Stations"

        if year:
            data = data[data.index.year == year]
            title += f" in {year}"

        if station:
            data = data[data["station"] == station]
            title += f" - station {station}"
        else:
            data = data[["adultCount", "aonCount"]].groupby(data.index).sum()

        fig, ax = plt.subplots(**kwargs)

        data["adultCount"].plot(
            ax=ax,
            color=ColorMap.c1,
            label="Visible adults",
            linewidth=2,
            linestyle=LineStyle.VisibleAdults,
        )

        data["aonCount"].plot(
            ax=ax,
            color=ColorMap.c2,
            label="Apparently occupied nests",
            linewidth=2,
            linestyle=LineStyle.ApperentlyOccupied,
        )

        self._style_plot(
            ax, title, data["adultCount"].max(), year_range=[year] if year else None
        )

        return fig

    def compare_years(self, station: str = None, **kwargs):
        """
        Compare kittiwake counts across years on a common calendar axis.

        Parameters
        ----------
        station : str, optional
            Filter by station.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure
        """
        data = self.resampled.copy()
        title = "Kittiwakes at City Stations"

        if station:
            data = data[data["station"] == station]
            title += f" - station {station}"
        else:
            data = data[["adultCount", "aonCount"]].groupby(data.index).sum()

        add_month_day_columns(data, inplace=True)

        fig, ax = plt.subplots(**kwargs)
        years = sorted(data["year"].unique())
        colors = ["c1", "c2", "c3", "c4", "c5", "cream"][: len(years)]
        color_handles = []

        for year, color in zip(years, colors):
            color = getattr(ColorMap, color)
            year_data = data[data["year"] == year].set_index("plot_date")
            year_data = year_data.where(year_data > 0)

            year_data["adultCount"].plot(
                ax=ax,
                linestyle=LineStyle.VisibleAdults,
                color=color,
            )
            year_data["aonCount"].plot(
                ax=ax,
                linestyle=LineStyle.ApperentlyOccupied,
                color=color,
            )

            color_handles.append(
                mlines.Line2D([], [], color=color, label=str(year), linestyle="-")
            )

        # Legends
        ax.legend(handles=color_handles, loc="upper left", fontsize=10, frameon=False)
        ax.add_artist(
            ax.legend(
                handles=[
                    mlines.Line2D(
                        [],
                        [],
                        color="black",
                        label="Visible adults",
                        linestyle=LineStyle.VisibleAdults,
                    ),
                    mlines.Line2D(
                        [],
                        [],
                        color="black",
                        label="Adults on nest",
                        linestyle=LineStyle.ApperentlyOccupied,
                    ),
                ],
                loc="lower right",
                fontsize=8,
                frameon=False,
            )
        )

        # Set axis limits
        self._style_plot(ax, title, data["adultCount"].max(), year_range=None)

        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-09-30"))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        fig.autofmt_xdate()

        return fig

    def _style_plot(self, ax, title, ymax, year_range=None):
        """
        Shared styling for plots.
        """
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylabel("Kittiwake count")
        ax.set_xlabel("")
        ax.set_ylim(0, ymax * 1.1)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.patch.set_alpha(0.0)

        if year_range:
            year = year_range[0]
            ax.set_xlim(pd.Timestamp(f"{year}-03-01"), pd.Timestamp(f"{year}-10-31"))

        # Add logo
        fig = ax.get_figure()
        logo_ax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")
        fig.patch.set_alpha(0.0)
