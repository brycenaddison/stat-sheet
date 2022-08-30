import requests
import json
import statistics
import datetime
import pandas
from typing import Any, Union, Optional


class Champions:
    def __init__(
        self, performances: dict = None, team_performances: dict = None
    ):
        """Initializes champion stats, can process data from
        dict[matchId, MatchDTO] from Riot Games match-v5 API

        Args:
            data (dict, optional): _description_. Defaults to None.
        """

        self.n = 0
        self.champions = {}
        self.matchids = []
        self.names = {
            int(v["key"]): v["name"]
            for (k, v) in requests.get(
                "http://ddragon.leagueoflegends.com/cdn/12.13.1/data/en_US/champion.json"
            )
            .json()["data"]
            .items()
        }
        if performances is not None and team_performances is not None:
            self.add_performances(performances)
            self.add_team_performances(team_performances)

    def add_performances(self, performances: dict[str, Any]):
        print("Extracting picks from performances...")
        for performance in performances:
            self.add_pick(performance)
        print("Picks extracted.")

    def add_team_performances(self, team_performances: dict[str, Any]):
        print("Extracting bans from team performances...")
        for team_performance in team_performances:
            if team_performance["matchId"] not in self.matchids:
                self.n += 1
                self.matchids.append(team_performance["matchId"])
            for ban in team_performance["bans"]:
                self.add_ban(
                    ban["championId"],
                    ban["pickTurn"],
                    team_performance["blueside"],
                )
        print("Bans extracted.")

    def verify_champion(self, championId: int) -> bool:
        """If champion is not in database, creates a new entry.

        Args:
            championId (int): championId from Riot

        Returns:
            bool: True if champion was already in database, False otherwise
        """

        if championId not in self.champions:
            self.champions[championId] = {
                "name": self.names[championId],
                "bans": {"blue": 0, "red": 0, "pickTurns": []},
                "picks": {
                    "win": 0,
                    "loss": 0,
                    "blue": 0,
                    "red": 0,
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "cs": 0,
                    "timePlayed": 0,
                    "damage": 0,
                    "gold": 0,
                    "xpd8": 0,
                    "gd8": 0,
                    "csd8": 0,
                    "xpd14": 0,
                    "gd14": 0,
                    "csd14": 0,
                    "games": [],
                },
            }
            return False
        return True

    def add_ban(self, championId: int, pickTurn: int, blueside: bool) -> None:
        """Increments ban stats for a given champion.

        Args:
            championId (int): championId of ban from Riot
            teamId (int): teamId of ban from Riot
            pickTurn (int): pickTurn of ban from Riot
        """

        self.verify_champion(championId)
        self.champions[championId]["bans"]["blue" if blueside else "red"] += 1
        self.champions[championId]["bans"]["pickTurns"].append(pickTurn)

    def add_pick(self, performance: dict[str, Any]) -> None:
        """Updates pick stats for a champion with stats from performance from API.

        Args:
            performance (dict[str, Any]): performance of champion pick
        """
        if performance["matchId"] not in self.matchids:
            self.n += 1
            self.matchids.append(performance["matchId"])
        championId = performance["champid"]
        team = "blue" if performance["blueside"] else "red"
        win = performance["win"]

        self.verify_champion(championId)
        pick_stats = self.champions[championId]["picks"]

        pick_stats["win" if win else "loss"] += 1
        pick_stats[team] += 1
        pick_stats["kills"] += performance["kills"]
        pick_stats["deaths"] += performance["deaths"]
        pick_stats["assists"] += performance["assists"]
        pick_stats["cs"] += performance["cs"]
        pick_stats["timePlayed"] += performance["time"]
        pick_stats["damage"] += performance["dmg"]
        pick_stats["gold"] += performance["gold"]
        # Bandage fix, ideally have separate game number
        pick_stats["csd8"] += (
            performance["csd8"] if type(performance["csd8"]) is int else 0
        )
        pick_stats["xpd8"] += (
            performance["xpd8"] if type(performance["xpd8"]) is int else 0
        )
        pick_stats["gd8"] += (
            performance["gd8"] if type(performance["gd8"]) is int else 0
        )
        pick_stats["csd14"] += (
            performance["csd14"] if type(performance["csd14"]) is int else 0
        )
        pick_stats["xpd14"] += (
            performance["xpd14"] if type(performance["xpd14"]) is int else 0
        )
        pick_stats["gd14"] += (
            performance["gd14"] if type(performance["gd14"]) is int else 0
        )

        pick_stats["games"].append(
            {
                "puuid": performance["puuid"],
                "position": performance["role"],
                "team": performance["team"],
                "matchId": performance["matchId"],
                "win": win,
                "kills": performance["kills"],
                "deaths": performance["deaths"],
                "assists": performance["assists"],
            }
        )

    def dump_data(self, filename: str = "output.json") -> None:
        """Dumps champion stats dict to json file.

        Args:
            filename (str, optional): File to output to. Defaults to
                "output.json".
        """

        print(f"Dumping data to {filename}")
        with open(filename, "w") as f:
            json.dump(self.champions, f, indent=4)

    def get_best_player(self, championId: int) -> Optional[dict[str, Any]]:
        """Calculates most prolific player on a champion from a list of games

        Args:
            championId (int): championId from Riot data

        Returns:
            Optional[dict[str, Any]]: dict of puuid, picks, winrate, and kda,
                None if no games are played
        """
        # TO-DO, make account for alt accounts
        self.verify_champion(championId)

        total_picks = (
            self.champions[championId]["picks"]["blue"]
            + self.champions[championId]["picks"]["red"]
        )
        if total_picks == 0:
            return None

        players = {}
        game_list = self.champions[championId]["picks"]["games"]

        for game in game_list:
            players.setdefault(
                game["puuid"],
                {
                    "puuid": game["puuid"],
                    "team": game["team"],
                    "wins": 0,
                    "losses": 0,
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                },
            )

            pd = players[game["puuid"]]
            pd["wins" if game["win"] else "losses"] += 1
            pd["kills"] += game["kills"]
            pd["deaths"] += game["deaths"]
            pd["assists"] += game["assists"]

        df = pandas.DataFrame.from_records(list(players.values()))

        df["kda"] = round((df["kills"] + df["assists"]) / df["deaths"], 1)
        df["games"] = df["wins"] + df["losses"]
        df["winrate"] = df["wins"] / df["games"]

        df = df.sort_values(
            ["wins", "kda", "losses", "kills"],
            ascending=[False, False, True, False],
            ignore_index=True,
        )

        return (
            df[["puuid", "team", "games", "winrate", "kda"]].iloc[0].to_dict()
        )

    def get_stat_summary(
        self, championId: int
    ) -> dict[str, Union[str, float]]:
        """Returns dict of summarized champion data.

        Args:
            championId (int): championId from Riot to fetch data for

        Returns:
            dict[str, float]: dict of statistics stored
        """

        self.verify_champion(championId)
        data = self.champions[championId]
        total_picks = data["picks"]["blue"] + data["picks"]["red"]
        total_bans = data["bans"]["blue"] + data["bans"]["red"]
        bt = data["bans"]["pickTurns"]

        if total_picks == 0:
            return {
                "name": data["name"],
                "picks": 0,
                "bans": total_bans,
                "presence": round(total_bans / self.n, 2),
                "wins": pandas.NA,
                "losses": pandas.NA,
                "winrate": pandas.NA,
                "kda": pandas.NA,
                "avg_ban": round(statistics.mean(bt), 1)
                if len(bt) != 0
                else pandas.NA,
                "gametime": pandas.NA,
                "csm": pandas.NA,
                "dpm": pandas.NA,
                "gpm": pandas.NA,
                "csd8": pandas.NA,
                "gd8": pandas.NA,
                "xpd8": pandas.NA,
                "csd14": pandas.NA,
                "gd14": pandas.NA,
                "xpd14": pandas.NA,
                "best_team": pandas.NA,
                "best_puuid": pandas.NA,
                "best_games": pandas.NA,
                "best_winrate": pandas.NA,
                "best_kda": pandas.NA,
            }

        player = self.get_best_player(championId)

        return {
            "name": data["name"],
            "picks": total_picks,
            "bans": total_bans,
            "presence": round((total_picks + total_bans) / self.n, 2),
            "wins": data["picks"]["win"],
            "losses": data["picks"]["loss"],
            "winrate": data["picks"]["win"] / total_picks,
            "kda": float("inf")
            if data["picks"]["deaths"] == 0
            else round(
                (data["picks"]["kills"] + data["picks"]["assists"])
                / data["picks"]["deaths"],
                1,
            ),
            "avg_ban": round(statistics.mean(bt), 1)
            if len(bt) != 0
            else pandas.NA,
            "gametime": datetime.timedelta(
                seconds=(data["picks"]["timePlayed"] / total_picks)
            ),
            "csm": round(
                data["picks"]["cs"] * 60 / data["picks"]["timePlayed"], 1
            ),
            "dpm": int(
                data["picks"]["damage"] * 60 / data["picks"]["timePlayed"]
            ),
            "gpm": int(
                data["picks"]["gold"] * 60 / data["picks"]["timePlayed"]
            ),
            "csd8": round(data["picks"]["csd8"] / total_picks, 1),
            "gd8": int(data["picks"]["gd8"] / total_picks),
            "xpd8": int(data["picks"]["xpd8"] / total_picks),
            "csd14": round(data["picks"]["csd14"] / total_picks, 1),
            "gd14": int(data["picks"]["gd14"] / total_picks),
            "xpd14": int(data["picks"]["xpd14"] / total_picks),
            "best_team": player["team"],
            "best_puuid": player["puuid"],
            "best_games": player["games"],
            "best_winrate": player["winrate"],
            "best_kda": player["kda"],
        }

    def dataframe(self) -> pandas.DataFrame:
        """Outputs champion stat summary as a dataframe

        Returns:
            pandas.DataFrame: Dataframe of champion summary stats
        """
        print("Exporting dataframe...")
        df = pandas.DataFrame()

        for champion in self.names.keys():
            summary = {
                x: [y] for x, y in self.get_stat_summary(champion).items()
            }

            df = pandas.concat(
                [
                    df,
                    pandas.DataFrame.from_dict(summary),
                ],
                ignore_index=True,
            )

        df.columns = [
            "Name",
            "Picks",
            "Bans",
            "Presence",
            "Wins",
            "Losses",
            "Winrate",
            "KDA",
            "AVG BT",
            "GT",
            "CS/M",
            "DPM",
            "GPM",
            "CSD@8",
            "GD@8",
            "XPD@8",
            "CSD@14",
            "GD@14",
            "XPD@14",
            "BP Team",
            "Best Player",
            "BP Picks",
            "BP Win%",
            "BP KDA",
        ]

        df = df.sort_values(
            ["Presence", "Picks", "Name"],
            ascending=[False, False, True],
            ignore_index=True,
        )

        print("Dataframe exported.")

        return df
