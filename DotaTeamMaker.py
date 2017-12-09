"""
   Copyright 2017 Jonathan "FusionDota2" Driessen

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import csv


def create_player_dicts():
    """
    This creates the player dictionary conataining the mmr, role and name
    from the csv file. A seperate dictionary is created for the captains.
    format {'Player_mmr': ['Player_name', 'Player_prefered_role']}
    A list containing the MMRs of the players competing is made and sorted
    from high to low.
    :return: Player and captain dictionaries, team_amount and mmr lists
    """
    players = list()
    captain_dict = dict()
    player_dict = dict()
    captain_mmr_list = list()
    player_mmr_list = list()
    with open('PlayerList.csv') as infile:
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
    player_mmr_list = sorted(player_mmr_list, reverse=True)
    captain_mmr_list = sorted(captain_mmr_list, reverse=True)
    return player_dict, captain_dict, player_mmr_list, captain_mmr_list, \
        team_amount


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
    global players_on_pref_role
    role_amounts = list()
    for i in range(6):
        role_amounts.append(0)
    for mmr in captain_mmr_list:
        role_amounts[int(captain_dict[mmr][1])] += 1
    for mmr in player_mmr_list:
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
    return player_dict, captain_dict


def distribute_captain(captain_dict, captain_mmr_list, team_amount):
    """
    Creates the empty teams in dictionary format and distributes the
    captains among them.
    :param captain_dict:
    :param captain_mmr_list:
    :param team_amount:
    :return: The teamlist, captain mmr list and team amount.
    """
    teamlist = list()
    for i in range(team_amount):
        teamlist.append(
            {'1': None, '2': None, '3': None, '4': None, '5': None, 'Avg': 0,
                'Playercount': 0})
    for team in teamlist:
        team.update({captain_dict[captain_mmr_list[0]][1]:
            captain_dict[captain_mmr_list[0]][0]})
        team.update({'Captain': captain_dict[captain_mmr_list[0]][0]})
        team.update({'Avg': captain_mmr_list[0]})
        team.update({'Playercount': 1})
        del captain_dict[int(captain_mmr_list[0])]
        captain_mmr_list.remove(captain_mmr_list[0])
    return teamlist, captain_mmr_list


def add_player_round(player_dict, player_mmr_list, teamlist, cur_round,
        current_player_index=None):
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
        return add_player_round(player_dict, player_mmr_list, teamlist,
            cur_round, current_player_index + 1)


def update_team_avg(team, added_mmr):
    team.update({'Avg': ((team['Avg'] * (team['Playercount'] - 1)) +
                         added_mmr) / team['Playercount']})


def master_excecute():
    pd, cd, pml, cml, ta = create_player_dicts()
    global players_on_pref_role
    players_on_pref_role = ta * 5
    distribute_roles(pd, cd, pml, cml, ta)
    tl, cml = distribute_captain(cd, cml, ta)
    players_added = 0
    for i in range(4):
        for cr in range(ta):
            add_player_round(pd, pml, tl, i + 1)
            players_added += 1
    minimum_avg = None
    maximum_avg = None
    for team in tl:
        del team['Playercount']
        if minimum_avg == None:
            minimum_avg = team['Avg']
        if maximum_avg == None:
            maximum_avg = team['Avg']
        if team['Avg'] < minimum_avg:
            minimum_avg = team['Avg']
        if team['Avg'] > maximum_avg:
            maximum_avg = team['Avg']
    print(tl)
    print(str(players_on_pref_role + ta)+ '/' + str(ta*5) + ' players are on '
                                                            'their preffered'
                                                            ' roles')
    print('There is a ' + str(maximum_avg - minimum_avg) + ' spread on the '
                                                           'averages')


master_excecute()
