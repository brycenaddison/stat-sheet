import requests
from stats.champions import Champions
from stats.players import Players
from stats.roster import Roster
from stats.teams import Teams
import pygsheets
import json
import os
import pandas


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


def get_property(team: str, property: str, teams: dict[str, any]):
    if team == "":
        return ""
    return list(filter(lambda item: item["code"] == team, teams))[0][property]


def percent(column):
    return column.apply(lambda x: "{:.0%}".format(x) if x != "" else "")


def time(x):
    return f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}"


def update_champs(
    champions: Champions, sheet: pygsheets.Spreadsheet, sheet_name: str, teams
):
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
        lambda x: f'=IMAGE("{get_property(x, "logo", teams)}")'
    )
    df.replace(float("inf"), "Perfect", inplace=True)

    roster = Roster()
    roster.load_data()
    df["Best Player"] = df["Best Player"].apply(roster.get_name)
    roster.dump_data()

    df.rename(
        columns={"BP Team": "Best Player", "Best Player": "BP"}, inplace=True
    )
    print(df)

    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(df, (1, 1))


def update_teams(
    teams: Teams, sheet: pygsheets.Spreadsheet, sheet_name: str, team_data
):
    df = teams.dataframe()
    nf = pandas.DataFrame()

    nf["Team"] = df["team"].apply(
        lambda x: f'=IMAGE("{get_property(x, "logo", team_data)}")'
    )
    nf["Team Code"] = df["team"]
    nf["Team Name"] = df["team"].apply(
        lambda x: get_property(x, "name", team_data)
    )
    nf["Games"] = df["n"]
    nf["Win Rate"] = percent(df["win%"])
    nf["Time"] = df["gt"].apply(time)
    nf["Blue Wins"] = df["bluewins"]
    nf["Blue Win%"] = percent(df["bwin%"])
    nf["Red Wins"] = df["redwins"]
    nf["Red Win%"] = percent(df["rwin%"])
    nf["K/D"] = percent(df["kd"])
    nf["Kills/g"] = df["k/g"].apply(lambda x: round(x, 2))
    nf["Deaths/g"] = df["d/g"].apply(lambda x: round(x, 2))
    nf["Assists/g"] = df["a/g"].apply(lambda x: round(x, 2))
    nf["Kills@15"] = df["k15"].apply(lambda x: round(x, 2))
    nf["Kills@25"] = df["k25"].apply(lambda x: round(x, 2))
    nf["FB%"] = percent(df["fb%"])
    nf["DMG/min"] = df["dmg/m"].apply(lambda x: round(x, 2))
    nf["Gold/min"] = df["g/m"].apply(lambda x: round(x, 2))
    nf["GD@14"] = df["gd14/g"].apply(lambda x: round(x, 2))
    nf["CS/min"] = df["cs/m"].apply(lambda x: round(x, 2))
    nf["CSD@14"] = df["csd14/g"].apply(lambda x: round(x, 2))
    nf["XP/min"] = df["xp/m"].apply(lambda x: round(x, 2))
    nf["XPD@14"] = df["xpd14/g"].apply(lambda x: round(x, 2))
    nf["VS/min"] = df["vs/m"].apply(lambda x: round(x, 2))
    nf["Ward/min"] = df["w/m"].apply(lambda x: round(x, 2))
    nf["CW/min"] = df["cw/m"].apply(lambda x: round(x, 2))
    nf["WC/min"] = df["wc/m"].apply(lambda x: round(x, 2))
    nf["WC%"] = percent(df["wc%"])
    nf["FT%"] = percent(df["ft%"])
    nf["Tower/g"] = df["t/g"].apply(lambda x: round(x, 2))
    nf["TG/g"] = df["ot/g"].apply(lambda x: round(x, 2))
    nf["FD%"] = percent(df["fd%"])
    nf["Drag%"] = percent(df["drag%"])
    nf["Drag/g"] = df["drag/g"].apply(lambda x: round(x, 2))
    nf["Rift%"] = percent(df["rift%"])
    nf["Rift/g"] = df["rift%"].apply(lambda x: round(x, 2))
    nf["Baron/g"] = df["b/g"].apply(lambda x: round(x, 2))
    nf["Baron%"] = percent(df["baron%"])

    nf = nf.sort_values(
        ["Win Rate", "Time"],
        ascending=[False, True],
        ignore_index=True,
    )
    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(nf, (1, 1))


def update_players(
    players: Players, sheet: pygsheets.Spreadsheet, sheet_name: str, team_data
):
    df = players.dataframe()
    nf = pandas.DataFrame()

    nf["Team"] = df["team"].apply(
        lambda x: f'=IMAGE("{get_property(x, "logo", team_data)}")'
    )
    nf["Team Code"] = df["team"]

    roster = Roster()
    roster.load_data()
    nf["Summoner Name"] = df["puuid"].apply(roster.get_name)
    roster.dump_data()

    roles = {
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "MIDDLE": "Middle",
        "BOTTOM": "Bottom",
        "UTILITY": "Support",
    }

    nf["Role"] = df["role"].apply(lambda x: roles[x])
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

    print(nf)
    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(nf, (1, 1))


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

    plat_players = Players(plat_performances)
    plat_champs = Champions(plat_performances, plat_teamperformances)
    plat_teams = Teams(plat_teamperformances)

    dia_players = Players(dia_performances)
    dia_champs = Champions(dia_performances, dia_teamperformances)
    dia_teams = Teams(dia_teamperformances)

    update_players(plat_players, plat_sheet, "Players", teams)
    update_players(dia_players, dia_sheet, "Players", teams)

    update_champs(plat_champs, plat_sheet, "Champions", teams)
    update_champs(dia_champs, dia_sheet, "Champions", teams)

    update_teams(plat_teams, plat_sheet, "Teams", teams)
    update_teams(plat_teams, dia_sheet, "Teams", teams)
