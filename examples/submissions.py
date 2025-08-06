# %%
from pathlib import Path
import numpy as np
import pandas as pd

from rissa_plotter.readers import FireBase

path = r"c:\work_projects\RissaCS\Kittiwalkers\ontvangen_phillip\rissa-app-firebase-adminsdk-fbsvc-c66690f67d.json"

with FireBase(path) as fb:
    city_data = fb.read_table("submissionsKittiwakesCity")
    hotel_data = fb.read_table("submissionsKittiwakesHotels")
    general_data = fb.read_table("submissionsKittiwakesGeneralHotels")
# %%

city_ids = np.unique(city_data["userId"])
hotel_ids = np.unique(hotel_data["userId"])
general_ids = np.unique(general_data["userId"])


unique_ids = np.unique(np.concatenate((city_ids, hotel_ids, general_ids)))

# %%
