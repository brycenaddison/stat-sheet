import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

RIOT_KEY = os.getenv("RIOT_KEY")


class Roster:
    def __init__(self, data: dict = None):
        self.rosters = {}

    def get_name(self, puuid: str):
        if type(puuid) is not str:
            return puuid
        if puuid == "":
            return puuid

        if puuid not in self.rosters.keys():
            self.rosters[puuid] = {
                "summonerName": self.fetch_summoner(puuid),
                "puuids": [puuid],
            }

        return self.rosters[puuid]["summonerName"]

    def dump_data(self, filename: str = "data/rosters.json") -> None:
        """Dumps champion stats dict to json file.

        Args:S
            filename (str, optional): File to output to. Defaults to
                "output.json".
        """

        print(f"Dumping data to {filename}")
        with open(filename, "w") as f:
            json.dump(self.rosters, f, indent=4)

    def load_data(self, filename: str = "data/rosters.json") -> None:
        """Loads roster data from json file

        Args:
            filename (str, optional): File path. Defaults to "data/rosters.json".
        """

        print(f"Loading data from {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            self.rosters = json.load(f)

    def fetch_summoner(self, puuid: str) -> str:
        print(f"Fetching {puuid}")
        summoner = requests.get(
            f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_KEY}"
        ).json()
        return summoner["name"]
