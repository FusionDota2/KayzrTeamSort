"""
 This program sorts players into teams for Dota2 tournaments.
 Copyright (C) 2017  Jonathan "Fusion" Driessen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see https://www.gnu.org/licenses/gpl.html.
"""

import csv
import sys


def create_player_dicts(PlayerList):
    """
    This creates the player dictionary conataining the mmr, role and name
    from the csv file. A seperate dictionary is created for the captains.
    format {'Player_mmr': ['Player_name', 'Player_prefered_role']}
    A list containing the MMRs of the players competing is made and sorted
    from high to low.
    If there are to many players. Lowest MMR players get kicked out.
    :return: Player and captain dictionaries, team_amount and mmr lists
    """
    players = list()
    captain_dict = dict()
    player_dict = dict()
    captain_mmr_list = list()
    player_mmr_list = list()
    teamless_player_list = list()
    with open(PlayerList) as infile:
        reader = csv.reader(infile, delimiter=';')
        for line in reader:
            if line[4] == 'True':
                players.append(line[:4])
        for player in players:
            player[1] = int(player[1])
            if player[3] == 'False':
                if player[1] in player_dict.keys():
                    player[1] += 1
                player_dict.update({player[1]: [player[0], player[2]]})
                player_mmr_list.append(player[1])
            else:
                if player[1] in captain_dict.keys():
                    player[1] += 1
                captain_dict.update({player[1]: [player[0], player[2]]})
                captain_mmr_list.append(player[1])
    team_amount = len(players) // 5
    if len(captain_mmr_list) != team_amount:
        while len(captain_mmr_list) < team_amount:
            captain_mmr_list.append(max(player_mmr_list))
            captain_dict.update(
                {max(player_mmr_list): player_dict[max(player_mmr_list)]})
            del player_dict[max(player_mmr_list)]
            player_mmr_list.remove(max(player_mmr_list))
        while (len(captain_mmr_list)) > team_amount:
            player_mmr_list.append(min(captain_mmr_list))
            player_dict.update(
                {min(captain_mmr_list): captain_dict[min(captain_mmr_list)]})
            del captain_dict[min(captain_mmr_list)]
            captain_mmr_list.remove(min(captain_mmr_list))
    while len(player_mmr_list) > team_amount * 4:
        teamless_player_list.append(player_dict[min(player_mmr_list)][0])
        del player_dict[min(player_mmr_list)]
        player_mmr_list.remove(min(player_mmr_list))
    player_mmr_list = sorted(player_mmr_list, reverse=True)
    captain_mmr_list = sorted(captain_mmr_list, reverse=True)
    return player_dict, captain_dict, player_mmr_list, captain_mmr_list, \
        team_amount, teamless_player_list


def create_team_dictionaries(team_amount):
    """
    Creates the empty teams in dictionary format.
    Example team format=
    {'1': Player1, '2': Player2, '3': Player3, '4': Player4, '5': Player5,
    'Avg': 3500, *'Playercount': 5*, 'Captain': 'Player1'})
    *Playercount* removed at the end of main.
    :param team_amount:
    :return List of empty teamms in dictionary format.:
    """
    teamlist = list()
    for i in range(team_amount):
        teamlist.append(
            {'1': None, '2': None, '3': None, '4': None, '5': None, 'Avg': 0,
                'Playercount': 0})
    return teamlist


def distribute_roles(player_dict, captain_dict, player_mmr_list,
        captain_mmr_list, team_amount):
    """
    Distributes the roles among players. Giving priority form high to low
    mmr players to get their preffered roles. Probably gonna add
    functionality for role preference order. Now it just goes through the
    roles from 1 to 5 starting going from high mmr to low mmr players.
    :param player_dict:
    :param captain_dict:
    :param player_mmr_list:
    :param captain_mmr_list:
    :param team_amount:
    :return: Player and captain list with everyone updated to their new role.
    """
    players_on_pref_role = team_amount * 5
    role_amounts = list()
    any_role_captain_mmr_list = list()
    any_role_player_mmr_list = list()
    for i in range(6):
        role_amounts.append(0)
    for mmr in captain_mmr_list:
        if captain_dict[mmr][1] == 'Any':
            any_role_captain_mmr_list.append(mmr)
        else:
            role_amounts[int(captain_dict[mmr][1])] += 1
    for mmr in player_mmr_list:
        if player_dict[mmr][1] == 'Any':
            any_role_player_mmr_list.append(mmr)
            continue
        cur_role = int(player_dict[mmr][1])
        if role_amounts[cur_role] < team_amount:
            role_amounts[cur_role] += 1
        else:
            for role in enumerate(role_amounts):
                if role[0] == 0:
                    continue
                elif role[1] < team_amount:
                    role_amounts[role[0]] += 1
                    player_dict.update({mmr: [player_dict[mmr][0], str(role[
                        0])]})
                    players_on_pref_role -= 1
                    break
    for mmr in any_role_captain_mmr_list:
        for role in enumerate(role_amounts):
            if role[0] == 0:
                continue
            elif role[1] < team_amount:
                role_amounts[role[0]] += 1
                captain_dict.update({mmr: [captain_dict[mmr][0], str(role[
                    0])]})
                break
    for mmr in any_role_player_mmr_list:
        for role in enumerate(role_amounts):
            if role[0] == 0:
                continue
            elif role[1] < team_amount:
                role_amounts[role[0]] += 1
                player_dict.update({mmr: [player_dict[mmr][0], str(role[
                    0])]})
                break
    return players_on_pref_role


def distribute_captain(captain_dict, captain_mmr_list, teamlist):
    """
    distributes the captains amongst the teams.
    :param teamlist:
    :param captain_dict:
    :param captain_mmr_list:
    :return: The teamlist, captain mmr list and team amount.
    """
    for team in teamlist:
        team.update({captain_dict[captain_mmr_list[0]][1]:
            captain_dict[captain_mmr_list[0]][0]})
        team.update({'Captain': captain_dict[captain_mmr_list[0]][0]})
        team.update({'Avg': captain_mmr_list[0]})
        team.update({'Playercount': 1})
        del captain_dict[int(captain_mmr_list[0])]
        captain_mmr_list.remove(captain_mmr_list[0])
    return None


def add_player(player_dict, player_mmr_list, teamlist, cur_round,
        current_player_index=None):
    """
    Takes the highest mmr player yet to be distributed and looks for the the
    team with the lowest mmr. If the team doesn't have a player yet on
    position that the highest mmr player would fill it adds them to the team
    and returns the new teamlist.
    If the lowest mmr team already has a player on that role it calls the
    function recusively now taking the second highest mmr player still
    to be distributed.
    :param player_dict:
    :param player_mmr_list:
    :param teamlist:
    :param cur_round:
    :param current_player_index:
    :return teamlist with one player added:
    """
    if current_player_index is None:
        current_player_index = 0
    current_player = player_dict[player_mmr_list[current_player_index]]
    min_team_avg = None
    min_team_avg_index = None
    for team in teamlist:
        if min_team_avg is None and team['Playercount'] == cur_round:
            min_team_avg = team['Avg']
            min_team_avg_index = teamlist.index(team)
        elif team['Playercount'] == cur_round:
            if team['Avg'] < min_team_avg:
                min_team_avg = team['Avg']
                min_team_avg_index = teamlist.index(team)
        else:
            continue
    if teamlist[min_team_avg_index][str(current_player[1])] is None:
        teamlist[min_team_avg_index].update(
            {str(current_player[1]): current_player[0]})
        update_team_avg(teamlist[min_team_avg_index],
            player_mmr_list[current_player_index])
        player_mmr_list.remove(player_mmr_list[current_player_index])
        teamlist[min_team_avg_index].update(
            {'Playercount': teamlist[min_team_avg_index]['Playercount'] + 1})
        return teamlist
    else:
        return add_player(player_dict, player_mmr_list, teamlist,
            cur_round, current_player_index + 1)


def update_team_avg(team, added_mmr):
    team.update({'Avg': ((team['Avg'] * (team['Playercount'] - 1)) +
                         added_mmr) / team['Playercount']})


def write_away(teamlist, max_spread, role_frac, teamless_player_list):
    """
    Writes the team data to a csv file (one is created if it doesn't exist yet)
    that includes the teamlist, max mmr spread and the fraction of players
    playing their preffered role.
    :param teamlist:
    :param max_spread:
    :param role_frac:
    """
    with open('Outfile.csv', mode='w+') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(['There is a maximum spread of ' + str(
            max_spread) + ' on the team MMR\'rs'])
        writer.writerow(
            [role_frac + ' People are playing their preffered roles'])
        i = 0
        for team in teamlist:
            i += 1
            writelist = list()
            writer.writerow(['Team ' + str(i)])
            for key in team.keys():
                writelist.append(str(key) + ':' + str(team[key]))
            writer.writerow(writelist)
        writer.writerow(['Players without a team:'])
        writer.writerow(teamless_player_list)


def __main__(PlayerList):
    pd, cd, pml, cml, ta, tlpl = create_player_dicts(PlayerList)
    total_players = ta * 5
    tl = create_team_dictionaries(ta)
    players_on_pref_role = distribute_roles(pd, cd, pml, cml, ta)
    distribute_captain(cd, cml, tl)
    players_added = 0
    for i in range(4):
        for cr in range(ta):
            add_player(pd, pml, tl, i + 1)
            players_added += 1
    minimum_avg = None
    maximum_avg = None
    for team in tl:
        del team['Playercount']
        if minimum_avg is None:
            minimum_avg = team['Avg']
        if maximum_avg is None:
            maximum_avg = team['Avg']
        if team['Avg'] < minimum_avg:
            minimum_avg = team['Avg']
        if team['Avg'] > maximum_avg:
            maximum_avg = team['Avg']
    max_spread = maximum_avg - minimum_avg
    players_on_role_frac = str(players_on_pref_role) + '/' + str(total_players)
    write_away(tl, max_spread, players_on_role_frac, tlpl)

if len(sys.argv) != 2:
    print('Please submit a (valid) playerlist file.')
else:
    __main__(sys.argv[1])
