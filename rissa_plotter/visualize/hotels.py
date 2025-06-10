import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter

from rissa_plotter import HotelData, util

logo = util.get_logo()
chelsea_font = util.get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class HotelPlotter:
    def __init__(self, hotel_data: HotelData, transparent: bool):
        self.data = hotel_data
        self.transparent = transparent

    def plot_chick_counts(self, hotels: list = None, month: int = None, **kwargs):
        """
        Plot stacked bar charts of chick counts per hotel.

        Parameters
        ----------
        hotels : list of str, optional
            List of hotel names to include. If None, use all available in the dataset.
        month : int, optional
            Month to filter the data on.
        kwargs : dict
            Additional keyword arguments passed to `plt.subplots`.
        """

        colors = [util.ColorMap.c2, util.ColorMap.c1, util.ColorMap.c6]
        columns = ["one_chick", "two_chicks", "three_chicks"]

        # Default to all hotels
        if hotels is None:
            hotels = self.data.hotels

        ncols = len(hotels)
        fig, axes = plt.subplots(ncols=ncols, sharey=True, **kwargs)

        if ncols == 1:
            axes = [axes]

        for i, (ax, hotel) in enumerate(zip(axes, hotels)):
            data = self.data.select_on(hotel=hotel, month=month)[columns]
            data.plot.bar(ax=ax, stacked=True, color=colors)

            # Clean axis aesthetics
            ax.set_ylabel("Number of nests with chicks")
            ax.set_xlabel("")
            ax.set_ylim(0, 30)
            ax.set_title("")  # Clear default pandas title
            ax.legend().remove()
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            # Hide y-axis on all but the first plot
            if i != 0:
                ax.spines["left"].set_visible(False)
                ax.tick_params(axis="y", left=False, labelleft=False)

            # Add hotel label below plot
            ax.text(
                0.5,
                -0.15,
                hotel,
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=10,
            )

            # transparent background
            if self.transparent:
                ax.patch.set_alpha(0.0)

        # Add shared legend
        handles = [
            mpatches.Patch(color=c, label=label.replace("_", " "))
            for c, label in zip(colors, columns)
        ]
        fig.legend(
            handles=handles,
            loc="upper left",
            frameon=False,
            fontsize=8,
            bbox_to_anchor=(0.12, 0.9),
        )

        # transparent background
        if self.transparent:
            fig.patch.set_alpha(0.0)
        # Add logo
        logo_ax = fig.add_axes([0.75, 0.8, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")

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
        ax.set_title("Submissions by Kittiwalkers at Hotels")
        ax.set_ylabel("Cumulative submissions per year")
        ax.set_xlabel("")
        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-9-30"))
        ax.set_ylim(0, 120)
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        ax.legend(frameon=False, loc="upper left")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.autofmt_xdate()

        # Add logo in new axis
        logo_ax = fig.add_axes([0.75, 0.8, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")

        # transparent background
        if self.transparent:
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)

        return fig
