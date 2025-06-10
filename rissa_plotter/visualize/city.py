import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.dates import DateFormatter

from rissa_plotter import util
from rissa_plotter import CityData

logo = util.get_logo()
chelsea_font = util.get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class CityPlotter:
    def __init__(self, city_data: CityData, transparent: bool):
        """
        Initialize CityPlotter with raw city data and prepare resampled version.
        """
        self.data = city_data
        self.transparent = transparent

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
        data = self.data.resampled
        title = "Kittiwakes at City Stations"

        if year:
            data = data[data.index.year == year]
            title += f" in {year}"

        if station:
            data = data[data["station"] == station]
            title += f" - station {station}"
        else:
            data = data[["adultCount", "aonCount"]].groupby(data.index).sum()
            data = data.where(data > 0)

        fig, ax = plt.subplots(**kwargs)

        data["adultCount"].plot(
            ax=ax,
            color=util.ColorMap.c1,
            label="Visible adults",
            linestyle="-",
        )

        data["aonCount"].plot(
            ax=ax,
            color=util.ColorMap.c2,
            label="Apparently occupied nests",
            linestyle="--",
        )

        self._style_plot(
            ax, title, data["adultCount"].max(), year_range=[year] if year else None
        )

        if self.transparent:
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)

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
        data = self.data.resampled
        data_cols = ["adultCount", "aonCount"]
        title = "Kittiwakes at City Stations"

        if station:
            data = data[data["station"] == station]
            title += f" - station {station}"
        else:
            data = data[data_cols].groupby(data.index).sum()

        util.add_month_day_columns(data, inplace=True)

        colors = [util.ColorMap.c2, util.ColorMap.c1, util.ColorMap.c6]
        years = self.data.years

        fig, ax = plt.subplots(**kwargs)
        for year, color in zip(years, colors):
            year_data = data[data["year"] == year].set_index("plot_date")

            year_data[data_cols] = year_data[data_cols].where(year_data[data_cols] > 0)

            year_data["adultCount"].plot(
                ax=ax,
                linestyle="-",
                color=color,
            )
            year_data["aonCount"].plot(
                ax=ax,
                linestyle="--",
                color=color,
            )

            if year == years[-1]:
                last_entry = year_data.iloc[[-1]]
                ax.scatter(
                    last_entry.index,
                    last_entry["adultCount"],
                    color=color,
                )
                ax.scatter(
                    last_entry.index,
                    last_entry["aonCount"],
                    color=color,
                )

        # Legend 1 - years
        handles_1 = [
            mlines.Line2D([], [], color=colors[0], label=str(years[0]), linestyle="-"),
            mlines.Line2D([], [], color=colors[1], label=str(years[1]), linestyle="-"),
            mlines.Line2D([], [], color=colors[2], label=str(years[2]), linestyle="-"),
        ]
        legend_1 = ax.legend(
            handles=handles_1, loc="upper left", fontsize=10, frameon=False
        )
        ax.add_artist(legend_1)

        # legend 2 - type
        handels_2 = [
            mlines.Line2D([], [], color="black", label="Visible adults", linestyle="-"),
            mlines.Line2D(
                [], [], color="black", label="Apperently Occupied", linestyle="--"
            ),
        ]
        ax.legend(
            handles=handels_2,
            loc="lower right",
            fontsize=8,
            frameon=False,
        )

        # Set axis limits
        self._style_plot(ax, title, data["adultCount"].max(), year_range=None)

        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-10-31"))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        fig.autofmt_xdate()

        # transparent background
        if self.transparent:
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)

        return fig

    def plot_submissions(self, **kwargs):
        # Define colors and years to plot
        colors = [util.ColorMap.c2, util.ColorMap.c1, util.ColorMap.c6]
        years = self.data.years

        # Create figure and axis
        fig, ax = plt.subplots(**kwargs)

        # Loop through each year and plot cumulative submissions
        for color, year in zip(colors, years):
            yearly_data = self.data.daily_submissions[
                self.data.daily_submissions["year"] == year
            ]
            yearly_data = util.add_month_day_columns(yearly_data)

            ax.plot(
                yearly_data["plot_date"],
                yearly_data["entry"].cumsum(),
                color=color,
                label=str(year),
            )

        # Format plot
        ax.set_title("Submissions by Kittiwalkers at City Stations")
        ax.set_ylabel("Cumulative submissions per year")
        ax.set_xlabel("")
        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-9-30"))
        ax.set_ylim(0, 1200)
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        ax.legend(frameon=False, loc="upper left")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.autofmt_xdate()

        # transparent background
        if self.transparent:
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)

        # Add logo in new axis
        logo_ax = fig.add_axes([0.75, 0.8, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")

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

        if year_range:
            year = year_range[0]
            ax.set_xlim(pd.Timestamp(f"{year}-03-01"), pd.Timestamp(f"{year}-10-31"))

        # Add logo
        fig = ax.get_figure()
        logo_ax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")
