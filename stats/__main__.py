import requests
from stats.champions import Champions
from stats.players import Players
from stats.roster import Roster
from stats.teams import Teams
from stats.teampage import TeamPage
import pygsheets
import json
import os
import pandas
import threading
import random


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
    nf["K/D"] = df["kd"].apply(lambda x: round(x, 2))
    nf["Kills/g"] = df["k/g"].apply(lambda x: round(x, 2))
    nf["Deaths/g"] = df["d/g"].apply(lambda x: round(x, 2))
    nf["Assists/g"] = df["a/g"].apply(lambda x: round(x, 2))
    nf["Kills@15"] = df["k15/g"].apply(lambda x: round(x, 2))
    nf["Kills@25"] = df["k25/g"].apply(lambda x: round(x, 2))
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

    wks = sheet.worksheet_by_title(sheet_name)
    wks.set_dataframe(df, (1, 1))


def update_teampages(
    teampage: TeamPage, players: Players, sheet: pygsheets.Spreadsheet
):
    # threads = []
    codes = teampage.team_codes()
    for team_code in codes:
        print(f"Updating team page for {team_code}")
        update_teampage(teampage, players, sheet, team_code)
    #     threads.append(
    #         threading.Thread(
    #             target=update_teampage,
    #             args=(
    #                 teampage,
    #                 players,
    #                 sheet,
    #                 team_code,
    #             ),
    #         )
    #     )
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()


def update_teampage(
    teampage: TeamPage,
    players: Players,
    sheet: pygsheets.Spreadsheet,
    code: str,
):

    team_name = teampage.team_name(code)
    wks = None

    try:
        wks = sheet.worksheet_by_title(team_name)
    except pygsheets.exceptions.WorksheetNotFound:
        print(f"No template page found for {team_name}")
        return

    wks.cell((2, 7)).value = code
    wks.cell((1, 1)).value = teampage.logo(code)
    print(f"Adding match history for {team_name}")
    match_history(code, teampage, wks, 21, 1)
    print(f"Adding bans for {team_name}")
    wks.set_dataframe(
        teampage.banned_by(code).head(15),
        (2, 10),
        copy_head=False,
    )
    wks.set_dataframe(
        teampage.banned_against(code).head(15), (2, 13), copy_head=False
    )
    print(f"Adding player list for {team_name}")
    wks.set_dataframe(
        teampage.playerlist(code, players).head(15), (2, 17), copy_head=False
    )
    print(f"Added {team_name}")

    #     for column in range(0, 15):
    #         cell = wks.cell((base_row + row, base_column + column))
    #         win_cells.append(cell) if win else lose_cells.append(cell)

    # wks.update_cells(win_cells, "userEnteredFormat/textFormat/bold")


def banned_by(
    code: str,
    teampage: TeamPage,
    wks: pygsheets.Worksheet,
    base_row: int,
    base_column: int,
):
    df = teampage.banned_by(code).head(15)
    wks.set_dataframe(df, (base_row, base_column), copy_head=False)


def banned_against(
    code: str,
    teampage: TeamPage,
    wks: pygsheets.Worksheet,
    base_row: int,
    base_column: int,
):
    df = teampage.banned_against(code).head(15)
    wks.set_dataframe(df, (base_row, base_column), copy_head=False)


def match_history(
    code: str,
    teampage: TeamPage,
    wks: pygsheets.Worksheet,
    base_row: int,
    base_column: int,
):
    df = teampage.short_history(code)

    wks.set_dataframe(df, (base_row, base_column), copy_head=False)

    # for row in df.index:
    #     result = df.loc[row, "result"]
    #     cell = wks.cell((row + base_row, base_column + 15))
    #     cell.color = (0, 1, 0, 0.3) if result == "Win" else (1, 0, 0, 0.4)


def main():
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
    plat_teamdata = get_data(
        "http://api.brycenaddison.com/teams/plat", "data/plat_teams.json"
    )
    dia_teamdata = get_data(
        "http://api.brycenaddison.com/teams/fri", "data/dia_teams.json"
    )

    gc = pygsheets.authorize(
        service_file="client_secret.json", retries=1000, seconds_per_quota=10
    )
    plat_sheet = gc.open_by_key("17bzMtkinBMWADMarb0gM1BBSGt_O4GPhQR7ANAOh-4g")
    dia_sheet = gc.open_by_key("1gdjQQycmcA25PraEaTn16O1tpL20I9edYN_Y_o67nMA")

    plat_players = Players(plat_performances, plat_teamdata)
    plat_champs = Champions(plat_performances, plat_teamperformances)
    plat_teams = Teams(plat_teamperformances)
    plat_page = TeamPage(
        plat_performances, plat_teamperformances, plat_teamdata
    )

    dia_players = Players(dia_performances, dia_teamdata)
    dia_champs = Champions(dia_performances, dia_teamperformances)
    dia_teams = Teams(dia_teamperformances)
    dia_page = TeamPage(dia_performances, dia_teamperformances, dia_teamdata)

    update_teampage(dia_page, dia_players, dia_sheet, "JD")
    update_teampages(plat_page, plat_players, plat_sheet)
    update_teampages(dia_page, dia_players, dia_sheet)

    update_players(plat_players, plat_sheet, "Players", plat_teamdata)
    update_players(dia_players, dia_sheet, "Players", dia_teamdata)

    update_champs(plat_champs, plat_sheet, "Champions", plat_teamdata)
    update_champs(dia_champs, dia_sheet, "Champions", dia_teamdata)

    update_teams(plat_teams, plat_sheet, "Teams", plat_teamdata)
    update_teams(dia_teams, dia_sheet, "Teams", dia_teamdata)


if __name__ == "__main__":
    main()
