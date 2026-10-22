import unittest

import pandas as pd

from loader import build_geo_dataframe, fetch_location_data, get_geolocator


class TestLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geolocator = get_geolocator()

    def test_valid_locations(self):
        # Known values from Google Maps. OpenStreetMap coordinates differ
        # slightly, so compare to 2 decimal places (roughly 1 km).
        expected = [
            ("Museum of Modern Art", 40.7618552, -73.9782438, "Museum"),
            ("USS Alabama Battleship Memorial Park",
             30.684373, -88.015316, "Park"),
        ]

        df = build_geo_dataframe([row[0] for row in expected],
                                 self.geolocator)

        self.assertEqual(len(df), len(expected))

        for (loc, lat, lon, place_type), (_, row) in zip(expected,
                                                         df.iterrows()):
            with self.subTest(location=loc):
                self.assertEqual(row["location"], loc)
                self.assertAlmostEqual(row["latitude"], lat, places=2)
                self.assertAlmostEqual(row["longitude"], lon, places=2)
                self.assertEqual(str(row["type"]).lower(),
                                 place_type.lower())

    def test_invalid_location(self):
        result = fetch_location_data(self.geolocator, "asdfqwer1234")

        # The location name is kept; everything else should be NA.
        self.assertEqual(result["location"], "asdfqwer1234")
        for key in ("latitude", "longitude", "type"):
            with self.subTest(field=key):
                self.assertTrue(pd.isna(result[key]),
                                f"{key} should be NA for a fake location.")

        # Same check on the final DataFrame.
        df = build_geo_dataframe(["asdfqwer1234"], self.geolocator)
        self.assertEqual(df.loc[0, "location"], "asdfqwer1234")
        self.assertTrue(
            df.loc[0, ["latitude", "longitude", "type"]].isna().all())


if __name__ == "__main__":
    unittest.main()
