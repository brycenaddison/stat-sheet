from stats.roster import Roster
from stats.players import Players
import requests
import pandas


class TeamPage:
    def __init__(
        self,
        performances: dict = None,
        teamperformances: dict = None,
        teams: dict = None,
    ):
        """Initializes champion stats, can process data from
        dict[matchId, MatchDTO] from Riot Games match-v5 API

        Args:
            data (dict, optional): _description_. Defaults to None.
        """
        self.data = teamperformances
        self.players = performances
        self.teams = teams
        self.ids = None
        self.names = None
        self.roster = Roster()
        self.roster.load_data()
        self.bans = {}
        self.bana = {}

    def short_history(self, teamcode):
        history = sorted(
            list(filter(lambda item: item["team"] == teamcode, self.data)),
            key=lambda k: (k["week"], k["game"], k["startTime"]),
            reverse=True,
        )

        table = {
            "top_champ": [],
            "top_player": [],
            "top_kda": [],
            "jg_champ": [],
            "jg_player": [],
            "jg_kda": [],
            "mid_champ": [],
            "mid_player": [],
            "mid_kda": [],
            "bot_champ": [],
            "bot_player": [],
            "bot_kda": [],
            "sup_champ": [],
            "sup_player": [],
            "sup_kda": [],
            "result": [],
            "opponent": [],
            "details": [],
        }

        for match in history:
            id = match["matchId"]

            top = self.perf(teamcode, id, "TOP")
            jg = self.perf(teamcode, id, "JUNGLE")
            mid = self.perf(teamcode, id, "MIDDLE")
            bot = self.perf(teamcode, id, "BOTTOM")
            sup = self.perf(teamcode, id, "UTILITY")

            table["top_champ"].append(
                "" if top is None else self.img(top["champid"])
            )
            table["top_player"].append(
                "" if top is None else self.name(top["puuid"])
            )
            table["top_kda"].append("" if top is None else self.kda(top))

            table["jg_champ"].append(
                "" if jg is None else self.img(jg["champid"])
            )
            table["jg_player"].append(
                "" if jg is None else self.name(jg["puuid"])
            )
            table["jg_kda"].append("" if jg is None else self.kda(jg))

            table["mid_champ"].append(
                "" if mid is None else self.img(mid["champid"])
            )
            table["mid_player"].append(
                "" if mid is None else self.name(mid["puuid"])
            )
            table["mid_kda"].append("" if mid is None else self.kda(mid))

            table["bot_champ"].append(
                "" if bot is None else self.img(bot["champid"])
            )
            table["bot_player"].append(
                "" if bot is None else self.name(bot["puuid"])
            )
            table["bot_kda"].append("" if bot is None else self.kda(bot))

            table["sup_champ"].append(
                "" if sup is None else self.img(sup["champid"])
            )
            table["sup_player"].append(
                "" if sup is None else self.name(sup["puuid"])
            )
            table["sup_kda"].append("" if sup is None else self.kda(sup))

            table["result"].append("Win" if match["win"] else "Loss")
            table["opponent"].append(self.team_name(match["opponent"]))
            details = f'=HYPERLINK("{self.link(match["matchId"])}", "Week {match["week"]} Game {match["game"]}")'
            if match["week"] == 14 or (
                match["conf"] == "fri" and match["week"] == 8
            ):
                details = f'=HYPERLINK("{self.link(match["matchId"])}", "Finals Game {match["game"]}")'
            elif match["conf"] == "fri" and match["week"] > 5:
                details = f'=HYPERLINK("{self.link(match["matchId"])}", "Round {match["week"] - 5} Game {match["game"]}")'
            elif match["week"] > 7:
                details = f'=HYPERLINK("{self.link(match["matchId"])}", "Round {match["week"] - 7} Game {match["game"]}")'
            table["details"].append(details)

        df = pandas.DataFrame(table)

        return df

    def set_ids(self):
        if self.ids is None:
            self.ids = {
                int(v["key"]): v["id"]
                for (k, v) in requests.get(
                    "http://ddragon.leagueoflegends.com/cdn/12.13.1/data/en_US/champion.json"
                )
                .json()["data"]
                .items()
            }

    def set_names(self):
        if self.names is None:
            self.names = {
                int(v["key"]): v["name"]
                for (k, v) in requests.get(
                    "http://ddragon.leagueoflegends.com/cdn/12.13.1/data/en_US/champion.json"
                )
                .json()["data"]
                .items()
            }

    def img(self, key):
        self.set_ids()
        return f'=IMAGE("http://ddragon.leagueoflegends.com/cdn/12.16.1/img/champion/{self.ids[key]}.png")'

    def perf(self, teamcode, matchId, role):
        result = list(
            filter(
                lambda item: item["team"] == teamcode
                and item["matchId"] == matchId
                and item["role"] == role,
                self.players,
            )
        )
        if len(result) == 0:
            return None
        return result[0]

    def kda(self, perf):
        k = perf["kills"]
        d = perf["deaths"]
        a = perf["assists"]
        return f"{k}/{d}/{a}"

    def name(self, puuid):
        return self.roster.get_name(puuid)

    def save(self):
        self.roster.dump_data()

    def team_name(self, code):
        return list(filter(lambda item: item["code"] == code, self.teams))[0][
            "name"
        ]

    def link(self, match_id):
        return f"http://api.brycenaddison.com/match/{match_id}"

    def logo(self, code):
        link = list(filter(lambda item: item["code"] == code, self.teams))[0][
            "logo"
        ]
        return f'=IMAGE("{link}")'

    def team_codes(self):
        return [team["code"] for team in self.teams]

    def banned_against(self, teamcode):
        games = list(
            filter(lambda item: item["opponent"] == teamcode, self.data)
        )

        return self.banned(games)

    def banned_by(self, teamcode):
        games = list(filter(lambda item: item["team"] == teamcode, self.data))

        return self.banned(games)

    def banned(self, games):
        bans = {}

        for game in games:
            for ban in game["bans"]:
                if ban["championId"] not in bans:
                    bans[ban["championId"]] = 1
                else:
                    bans[ban["championId"]] += 1

        table = {"icon": [], "name": [], "count": []}

        for champId, count in bans.items():
            table["icon"].append(self.img(champId))
            table["name"].append(self.champ_name(champId))
            table["count"].append(count)

        return pandas.DataFrame(table).sort_values(
            ["count"],
            ascending=[False],
            ignore_index=True,
        )

    def champ_name(self, key):
        self.set_names()
        return self.names[key]

    def playerlist(self, teamcode, players: Players):
        df = players.dataframe()
        df = df[df["Team Code"] == teamcode][
            ["Name", "Role", "Games", "KDA", "KP%", "DMG%", "Gold%", "VS%"]
        ].sort_values(
            ["Games", "KDA"], ascending=[False, False], ignore_index=True
        )
        return df
