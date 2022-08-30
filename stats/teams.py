import json
import pandas
import datetime


class Teams:
    def __init__(self, data: dict = None):
        """Initializes champion stats, can process data from
        dict[matchId, MatchDTO] from Riot Games match-v5 API

        Args:
            data (dict, optional): _description_. Defaults to None.
        """
        self.teams = {}
        if data is not None:
            self.add_all_performances(data)

    def verify_team(self, team):
        if team not in self.teams:
            self.teams[team] = {
                "team": team,
                "n": 0,
                "wins": 0,
                "losses": 0,
                "time": 0,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "cs": 0,
                "gold": 0,
                "xp": 0,
                "dmg": 0,
                "vs": 0,
                "w": 0,
                "cw": 0,
                "wc": 0,
                "ow": 0,
                "fb": 0,
                "gd14": 0,
                "xpd14": 0,
                "csd14": 0,
                "k15": 0,
                "a15": 0,
                "d15": 0,
                "k25": 0,
                "a25": 0,
                "d25": 0,
                "fbarons": 0,
                "fdragons": 0,
                "ftowers": 0,
                "fheralds": 0,
                "barons": 0,
                "dragons": 0,
                "towers": 0,
                "heralds": 0,
                "obarons": 0,
                "odragons": 0,
                "oheralds": 0,
                "otowers": 0,
                "bluewins": 0,
                "bluegames": 0,
                "redwins": 0,
                "redgames": 0,
            }

    def add_performance(self, p):
        d = self.teams[p["team"]]
        d["n"] += 1
        d["wins" if p["win"] else "losses"] += 1
        d["time"] += p["time"]
        d["kills"] += p["k"]
        d["deaths"] += p["d"]
        d["assists"] += p["a"]
        d["cs"] += p["cs"]
        d["gold"] += p["gold"]
        d["xp"] += p["xp"]
        d["dmg"] += p["dmg"]
        d["vs"] += p["vs"]
        d["w"] += p["w"]
        d["cw"] += p["cw"]
        d["wc"] += p["wc"]
        d["ow"] += p["ow"]
        d["fb"] += 1 if p["fb"] else 0
        d["gd14"] += p["gd14"]
        d["xpd14"] += p["xpd14"]
        d["csd14"] += p["csd14"]
        d["k15"] += p["k15"]
        d["a15"] += p["a15"]
        d["d15"] += p["d15"]
        d["k25"] += p["k25"]
        d["a25"] += p["a25"]
        d["d25"] += p["d25"]
        d["fbarons"] += 1 if p["bFirst"] else 0
        d["fdragons"] += 1 if p["dFirst"] else 0
        d["ftowers"] += 1 if p["tFirst"] else 0
        d["fheralds"] += 1 if p["hFirst"] else 0
        d["barons"] += p["bKills"]
        d["dragons"] += p["dKills"]
        d["towers"] += p["tKills"]
        d["heralds"] += p["hKills"]
        d["obarons"] += p["bGiven"]
        d["odragons"] += p["dGiven"]
        d["oheralds"] += p["hGiven"]
        d["otowers"] += p["tGiven"]
        d["bluewins"] += 1 if (p["blueside"] and p["win"]) else 0
        d["bluegames"] += 1 if p["blueside"] else 0
        d["redwins"] += 1 if (not p["blueside"] and p["win"]) else 0
        d["redgames"] += 0 if p["blueside"] else 1

    def add_all_performances(self, data):
        for p in data:
            self.verify_team(p["team"])
            self.add_performance(p)

    def dump_data(self, filename: str = "output.json") -> None:
        """Dumps champion stats dict to json file.

        Args:
            filename (str, optional): File to output to. Defaults to
                "output.json".
        """

        print(f"Dumping data to {filename}")
        with open(filename, "w") as f:
            json.dump(self.players, f, indent=4)

    def dataframe(self) -> pandas.DataFrame:
        """Outputs champion stat summary as a dataframe

        Returns:
            pandas.DataFrame: Dataframe of champion summary stats
        """
        print("Exporting dataframe...")
        df = pandas.DataFrame().from_records(list(self.teams.values()))

        df["win%"] = df["wins"] / df["n"]
        df["gt"] = (df["time"] / df["n"]).apply(
            lambda x: datetime.timedelta(seconds=x)
        )
        df["kd"] = (df["kills"]) / df["deaths"]
        df["k/g"] = df["kills"] / df["n"]
        df["d/g"] = df["deaths"] / df["n"]
        df["a/g"] = df["assists"] / df["n"]
        df["cs/m"] = df["cs"] * 60 / df["time"]
        df["g/m"] = df["gold"] * 60 / df["time"]
        df["dmg/m"] = df["dmg"] * 60 / df["time"]
        df["xp/m"] = df["xp"] * 60 / df["time"]
        df["vs/m"] = df["vs"] * 60 / df["time"]
        df["w/m"] = df["w"] * 60 / df["time"]
        df["cw/m"] = df["cw"] * 60 / df["time"]
        df["wc/m"] = df["wc"] * 60 / df["time"]
        df["wc%"] = df["wc"] / df["ow"]
        df["gd14/g"] = df["gd14"] / df["n"]
        df["xpd14/g"] = df["xpd14"] / df["n"]
        df["csd14/g"] = df["csd14"] / df["n"]
        df["fb%"] = df["fb"] / df["n"]
        df["ft%"] = df["ftowers"] / df["n"]
        df["fd%"] = df["fdragons"] / df["n"]
        df["drag%"] = df["dragons"] / (df["dragons"] + df["odragons"])
        df["rift%"] = df["heralds"] / (df["heralds"] + df["oheralds"])
        df["baron%"] = df["barons"] / (df["barons"] + df["obarons"])
        df["t/g"] = df["towers"] / df["n"]
        df["ot/g"] = df["otowers"] / df["n"]
        df["d/g"] = df["dragons"] / df["n"]
        df["h/g"] = df["heralds"] / df["n"]
        df["b/g"] = df["barons"] / df["n"]
        df["bwin%"] = df["bluewins"] / df["bluegames"]
        df["rwin%"] = df["redwins"] / df["redgames"]
        print("Dataframe exported.")

        return df
