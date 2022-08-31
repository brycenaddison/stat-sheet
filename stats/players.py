import json
import pandas
from stats.roster import Roster


class Players:
    def __init__(self, data: dict = None, teams: dict = None):
        """Initializes champion stats, can process data from
        dict[matchId, MatchDTO] from Riot Games match-v5 API

        Args:
            data (dict, optional): _description_. Defaults to None.
        """
        self.players = {}
        self.teams = teams
        self.roster = Roster()
        self.roster.load_data()
        if data is not None:
            self.add_all_performances(data)

    def verify_player(self, puuid, team, role):
        key = "" + puuid + team + role
        if key not in self.players:
            self.players[key] = {
                "puuid": puuid,
                "team": team,
                "role": role,
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
                "solokills": 0,
                "fb": 0,
                "fbv": 0,
                "doubles": 0,
                "triples": 0,
                "quadras": 0,
                "pentas": 0,
                "gold8": 0,
                "xp8": 0,
                "cs8": 0,
                "gold14": 0,
                "xp14": 0,
                "cs14": 0,
                "gd8": 0,
                "xpd8": 0,
                "csd8": 0,
                "gd14": 0,
                "xpd14": 0,
                "csd14": 0,
                "k15": 0,
                "a15": 0,
                "d15": 0,
                "k25": 0,
                "a25": 0,
                "d25": 0,
                "jgmins": 0,
                "tk": 0,
                "td": 0,
                "ta": 0,
                "tgold": 0,
                "tdmg": 0,
                "tvs": 0,
                "tk15": 0,
                "td15": 0,
                "ta15": 0,
                "tk25": 0,
                "td25": 0,
                "ta25": 0,
                "picks": {},
            }

    def add_performance(self, p):
        key = "" + p["puuid"] + p["team"] + p["role"]
        d = self.players[key]
        d["n"] += 1
        d["wins" if p["win"] else "losses"] += 1
        d["time"] += p["time"]
        d["kills"] += p["kills"]
        d["deaths"] += p["deaths"]
        d["assists"] += p["assists"]
        d["cs"] += p["cs"]
        d["gold"] += p["gold"]
        d["xp"] += p["xp"]
        d["dmg"] += p["dmg"]
        d["vs"] += p["vs"]
        d["w"] += p["w"]
        d["cw"] += p["cw"]
        d["wc"] += p["wc"]
        d["solokills"] += p["solokills"]
        d["fb"] += 1 if p["fb"] else 0
        d["fbv"] += 1 if p["fbv"] else 0
        d["doubles"] += p["doubles"]
        d["triples"] += p["triples"]
        d["quadras"] += p["quadras"]
        d["pentas"] += p["pentas"]
        d["gold8"] += p["gold8"]
        d["xp8"] += p["xp8"]
        d["cs8"] += p["cs8"]
        d["gold14"] += p["gold14"]
        d["xp14"] += p["xp14"]
        d["cs14"] += p["cs14"]
        d["gd8"] += p["gd8"]
        d["xpd8"] += p["xpd8"]
        d["csd8"] += p["csd8"]
        d["gd14"] += p["gd14"]
        d["xpd14"] += p["xpd14"]
        d["csd14"] += p["csd14"]
        d["k15"] += p["k15"]
        d["a15"] += p["a15"]
        d["d15"] += p["d15"]
        d["k25"] += p["k25"]
        d["a25"] += p["a25"]
        d["d25"] += p["d25"]
        d["jgmins"] += p["jgmins"] if p["jgmins"] is not None else 0
        d["tk"] += p["tk"]
        d["td"] += p["td"]
        d["ta"] += p["ta"]
        d["tgold"] += p["tgold"]
        d["tdmg"] += p["tdmg"]
        d["tvs"] += p["tvs"]
        d["tk15"] += p["tk15"]
        d["td15"] += p["td15"]
        d["ta15"] += p["ta15"]
        d["tk25"] += p["tk25"]
        d["td25"] += p["td25"]
        d["ta25"] += p["ta25"]
        if p["champid"] not in d["picks"]:
            d["picks"][p["champid"]] = 1
        else:
            d["picks"][p["champid"]] += 1

    def add_all_performances(self, data):
        for p in data:
            self.verify_player(p["puuid"], p["team"], p["role"])
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

        def get_property(team: str, property: str, teams: dict[str, any]):
            if team == "":
                return ""
            try:
                return list(filter(lambda item: item["code"] == team, teams))[
                    0
                ][property]
            except IndexError:
                print(json.dumps(teams, indent=4))
                print(team)
                raise IndexError

        def percent(column):
            return column.apply(
                lambda x: "{:.0%}".format(x) if x != "" else ""
            )

        def time(x):
            return f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}"

        df = pandas.DataFrame().from_records(list(self.players.values()))

        df["kda"] = (df["kills"] + df["assists"]) / df["deaths"]
        df["dmg/gold"] = df["dmg"] / df["gold"]
        df["cs/m"] = df["cs"] * 60 / df["time"]
        df["g/m"] = df["gold"] * 60 / df["time"]
        df["dmg/m"] = df["dmg"] * 60 / df["time"]
        df["vs/m"] = df["vs"] * 60 / df["time"]
        df["w/m"] = df["w"] * 60 / df["time"]
        df["cw/m"] = df["cw"] * 60 / df["time"]
        df["wc/m"] = df["wc"] * 60 / df["time"]
        df["k/g"] = df["kills"] / df["n"]
        df["d/g"] = df["deaths"] / df["n"]
        df["a/g"] = df["assists"] / df["n"]
        df["ka15/g"] = (df["k15"] + df["a15"]) / df["n"]
        df["ka25/g"] = (df["k25"] + df["a25"]) / df["n"]
        df["kp15"] = (df["k15"] + df["a15"]) / df["tk15"]
        df["kp25"] = (df["k25"] + df["a25"]) / df["tk25"]
        df["kp"] = (df["kills"] + df["assists"]) / df["tk"]
        df["gd8/g"] = df["gd8"] / df["n"]
        df["xpd8/g"] = df["xpd8"] / df["n"]
        df["csd8/g"] = df["csd8"] / df["n"]
        df["gd14/g"] = df["gd14"] / df["n"]
        df["xpd14/g"] = df["xpd14"] / df["n"]
        df["csd14/g"] = df["csd14"] / df["n"]
        df["kill%"] = df["kills"] / df["tk"]
        df["death%"] = df["deaths"] / df["td"]
        df["fb%"] = df["fb"] / df["n"]
        df["fbv%"] = df["fbv"] / df["n"]
        df["jp%"] = df["jgmins"] / (13 * df["n"])
        df["gold%"] = df["gold"] / df["tgold"]
        df["dmg%"] = df["dmg"] / df["tdmg"]
        df["vs%"] = df["vs"] / df["tvs"]

        roles = {
            "TOP": "Top",
            "JUNGLE": "Jungle",
            "MIDDLE": "Middle",
            "BOTTOM": "Bottom",
            "UTILITY": "Support",
        }

        df["role"] = df["role"].apply(lambda x: roles[x])

        nf = pandas.DataFrame()

        nf["Team"] = df["team"].apply(
            lambda x: f'=IMAGE("{get_property(x, "logo", self.teams)}")'
        )
        nf["Team Code"] = df["team"]

        nf["Name"] = df["puuid"].apply(self.roster.get_name)
        self.roster.dump_data()

        nf["Role"] = df["role"]
        nf["Games"] = df["n"]
        nf["Win Rate"] = percent(df["wins"] / df["n"])
        nf["KDA"] = df["kda"].apply(lambda x: round(x, 2))
        nf["Kills"] = df["kills"]
        nf["Deaths"] = df["deaths"]
        nf["Assists"] = df["assists"]
        nf["Avg Kills"] = df["k/g"].apply(lambda x: round(x, 2))
        nf["Avg Deaths"] = df["d/g"].apply(lambda x: round(x, 2))
        nf["Avg Assists"] = df["a/g"].apply(lambda x: round(x, 2))
        nf["CS/min"] = df["cs/m"].apply(lambda x: round(x, 2))
        nf["Gold/min"] = df["g/m"].apply(lambda x: round(x, 2))
        nf["Gold%"] = percent(df["gold%"])
        nf["KP%"] = percent(df["kp"])
        nf["JP%"] = percent(df["jp%"])
        nf["DMG%"] = percent(df["dmg%"])
        nf["DMG/Gold"] = df["dmg/gold"].apply(lambda x: round(x, 2))
        nf["DMG/min"] = df["dmg/m"].apply(lambda x: round(x, 2))
        nf["VS/min"] = df["vs/m"].apply(lambda x: round(x, 2))
        nf["W/min"] = df["w/m"].apply(lambda x: round(x, 2))
        nf["WC/min"] = df["wc/m"].apply(lambda x: round(x, 2))
        nf["CW/min"] = df["cw/m"].apply(lambda x: round(x, 2))
        nf["VS%"] = percent(df["vs%"])
        nf["GD@8"] = df["gd8/g"].apply(lambda x: round(x, 2))
        nf["CSD@8"] = df["csd8/g"].apply(lambda x: round(x, 2))
        nf["XPD@8"] = df["xpd8/g"].apply(lambda x: round(x, 2))
        nf["GD@14"] = df["gd14/g"].apply(lambda x: round(x, 2))
        nf["CSD@14"] = df["csd14/g"].apply(lambda x: round(x, 2))
        nf["XPD@14"] = df["xpd14/g"].apply(lambda x: round(x, 2))
        nf["K+A@15"] = df["ka15/g"].apply(lambda x: round(x, 2))
        nf["KP%@15"] = percent(df["kp15"])
        nf["K+A@25"] = df["ka25/g"].apply(lambda x: round(x, 2))
        nf["KP%@25"] = percent(df["kp25"])
        nf["FB%"] = percent(df["fb%"])
        nf["FB Victim"] = percent(df["fbv%"])
        nf["Kill%"] = percent(df["kill%"])
        nf["Death%"] = percent(df["death%"])
        nf["Solo Kills"] = df["solokills"]
        nf["Doubles"] = df["doubles"]
        nf["Triples"] = df["triples"]
        nf["Quadras"] = df["quadras"]
        nf["Pentakills"] = df["pentas"]

        nf = nf.sort_values(
            ["Kills", "Games", "Win Rate"],
            ascending=[False, False, False],
            ignore_index=True,
        )
        nf.replace(float("inf"), "Perfect", inplace=True)

        print("Dataframe exported.")

        return nf
