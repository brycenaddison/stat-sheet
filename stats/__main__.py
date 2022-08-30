import requests
import stats.champions
import stats.players
import stats.roster
import pygsheets
import json
import os


def download_data(url, filename):
    print(f"Downloading matches from {url} to {filename}")
    matches = requests.get(url).json()
    with open(filename, "w") as f:
        json.dump(matches, f, indent=4)
    return matches


def get_data(url, filename):
    if os.path.exists(filename):
        print(f"Importing matches from {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return download_data(url, filename)


def update_champs(p, tp, sheet: pygsheets.Spreadsheet, sheet_name: str, teams):
    champions = stats.champions.Champions(performances=p, team_performances=tp)
    df = champions.dataframe().fillna("")
    df["Presence"] = df["Presence"].apply(
        lambda x: "{:.0%}".format(x) if x != "" else ""
    )
    df["Winrate"] = df["Winrate"].apply(
        lambda x: "{:.0%}".format(x) if x != "" else ""
    )
    df["BP Win%"] = df["BP Win%"].apply(
        lambda x: "{:.0%}".format(x) if x != "" else ""
    )
    df["GT"] = df["GT"].apply(
        lambda x: f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}"
        if x != ""
        else ""
    )
    df["BP Team"] = df["BP Team"].apply(
        lambda x: f'=IMAGE("{get_img_link(x, teams)}")'
    )
    df.replace(float("inf"), "Perfect", inplace=True)

    roster = stats.roster.Roster()
    roster.load_data()
    df["Best Player"] = df["Best Player"].apply(roster.get_name)
    roster.dump_data()

    df.rename(
        columns={"BP Team": "Best Player", "Best Player": "BP"}, inplace=True
    )
    print(df)

    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(df, (1, 1))


def get_img_link(team: str, teams: dict[str, any]):
    if team == "":
        return ""
    return list(filter(lambda item: item["code"] == team, teams))[0]["logo"]


def update_players(
    performances, sheet: pygsheets.Spreadsheet, sheet_name: str
):
    players = stats.players.Players(data=performances)
    df = players.dataframe()
    roster = stats.roster.Roster()
    roster.load_data()
    df["puuid"] = df["puuid"].apply(roster.get_name)
    roster.dump_data()

    df["kda"] = (df["kills"] + df["assists"]) / df["deaths"]
    df["cs/m"] = df["cs"] * 60 / df["time"]
    df["g/m"] = df["gold"] * 60 / df["time"]
    df["dmg/m"] = df["dmg"] * 60 / df["time"]
    df["vs/m"] = df["vs"] * 60 / df["time"]
    df["k/g"] = df["kills"] / df["n"]
    df["d/g"] = df["deaths"] / df["n"]
    df["a/g"] = df["assists"] / df["n"]
    df["gd8/g"] = df["gd8"] / df["n"]
    df["xpd8/g"] = df["xpd8"] / df["n"]
    df["csd8/g"] = df["csd8"] / df["n"]
    df["gd14/g"] = df["gd14"] / df["n"]
    df["xpd14/g"] = df["xpd14"] / df["n"]
    df["csd14/g"] = df["csd14"] / df["n"]
    df["fb%"] = df["fb"] / df["n"]
    df["fbv%"] = df["fbv"] / df["n"]
    df["jp%"] = df["jgmins"] / (13 * df["n"])

    print(df)
    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(df, (1, 1))


if __name__ == "__main__":
    plat_performances = get_data(
        "http://api.brycenaddison.com/performances/plat",
        "data/platperformances.json",
    )
    plat_teamperformances = get_data(
        "http://api.brycenaddison.com/teamperformances/plat",
        "data/platteamperformances.json",
    )
    dia_performances = get_data(
        "http://api.brycenaddison.com/performances/fri",
        "data/diaperformances.json",
    )
    dia_teamperformances = get_data(
        "http://api.brycenaddison.com/teamperformances/fri",
        "data/diateamperformances.json",
    )
    teams = get_data("http://api.brycenaddison.com/teams", "data/teams.json")

    gc = pygsheets.authorize(service_file="client_secret.json")
    plat_sheet = gc.open_by_key("17bzMtkinBMWADMarb0gM1BBSGt_O4GPhQR7ANAOh-4g")
    dia_sheet = gc.open_by_key("1gdjQQycmcA25PraEaTn16O1tpL20I9edYN_Y_o67nMA")

    update_players(plat_performances, plat_sheet, "Players")
    update_players(dia_performances, dia_sheet, "Players")
    update_champs(
        plat_performances,
        plat_teamperformances,
        plat_sheet,
        "Champions",
        teams,
    )
    update_champs(
        dia_performances, dia_teamperformances, dia_sheet, "Champions", teams
    )
