"""
Script to load geographical data into a pandas DataFrame, and save it as a
CSV file.
"""

import numpy as np
import pandas as pd
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim


def get_geolocator(agent="h501-student"):
    """
    Initiate a Nominatim geolocator instance given an `agent`.

    Parameters
    ----------
    agent : str, optional
        Agent name for Nominatim, by default 'h501-student'

    Returns
    -------
    geopy.geocoders.Nominatim
        A geolocator instance.
    """
    return Nominatim(user_agent=agent)


def fetch_location_data(geolocator, loc):
    """
    Look up a single location and return its geographic data.

    Parameters
    ----------
    geolocator : geopy.geocoders.Nominatim
        Geolocator used to look up the location.
    loc : str
        Name of the location to look up.

    Returns
    -------
    dict
        Keys 'location', 'latitude', 'longitude', and 'type'. If the
        location cannot be found (or the lookup fails), every value except
        'location' is NaN.
    """
    empty = {
        "location": loc,
        "latitude": np.nan,
        "longitude": np.nan,
        "type": np.nan,
    }

    try:
        location = geolocator.geocode(loc, timeout=10)
    except GeopyError as err:
        # Timeouts, rate limits, and service errors all subclass GeopyError.
        print(f"Could not geocode {loc!r}: {err}")
        return empty

    if location is None:
        return empty

    # geopy's Location has no `geo_type` attribute; the place type
    # (e.g. 'museum', 'park') lives in the raw Nominatim response.
    place_type = location.raw.get("type")

    return {
        "location": loc,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "type": place_type.title() if place_type else np.nan,
    }


def build_geo_dataframe(locations, geolocator=None):
    """
    Build a DataFrame of geographic data for a list of locations.

    Parameters
    ----------
    locations : list of str
        Location names to look up.
    geolocator : geopy.geocoders.Nominatim, optional
        Geolocator to use. A new one is created if not given.

    Returns
    -------
    pandas.DataFrame
        One row per location with columns 'location', 'latitude',
        'longitude', and 'type'.
    """
    if geolocator is None:
        geolocator = get_geolocator()

    geo_data = [fetch_location_data(geolocator, loc) for loc in locations]

    return pd.DataFrame(geo_data)


class GeoLoader:
    """
    Bonus: class-based version of the loader.

    Parameters
    ----------
    agent : str, optional
        Agent name for Nominatim, by default 'h501-student'
    """

    def __init__(self, agent="h501-student"):
        self.geolocator = get_geolocator(agent)

    def fetch(self, loc):
        """Return geographic data for a single location as a dict."""
        return fetch_location_data(self.geolocator, loc)

    def build_dataframe(self, locations):
        """Return a DataFrame of geographic data for a list of locations."""
        return build_geo_dataframe(locations, self.geolocator)

    def save_csv(self, locations, path="./geo_data.csv"):
        """Build the DataFrame for `locations`, save it to `path`, return it."""
        df = self.build_dataframe(locations)
        df.to_csv(path, index=False)
        return df


if __name__ == "__main__":
    loader = GeoLoader()

    locations = [
        "Museum of Modern Art",
        "iuyt8765(*&)",
        "Alaska",
        "Franklin's Barbecue",
        "Burj Khalifa",
    ]

    print(loader.save_csv(locations))
