import numpy as np


def assign_to_nearest(timestamp, fixed_dates):
    diffs = np.abs(fixed_dates - timestamp)  # ← works in all pandas versions
    return fixed_dates[diffs.argmin()]
