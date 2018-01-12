"""
 This program sorts players into teams for Dota2 tournaments.
 Copyright (C) 2018  Jonathan "Fusion" Driessen

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

# This is the version that distributes the lowest mmr players that want
# to support first.

import csv
import sys


def create_player_dicts(playerfile):
    """
    This creates the player dictionary conataining the mmr, role and name
    from the csv file. a seperate dictionary is created for the captains.
    format {'Player_mmr': ['Player_name', 'Player_prefered_role']}
    A list containing the MMRs of the players competing is made and sorted
    from high to low. = 'XXXXXX_mmr_list'
    If there are to many players. Lowest MMR players get kicked out.
    :return: Player and captain dictionaries, team_amount and mmr lists
    """
    players = list()
    captain_dict = dict()
    player_dict = dict()
    captain_mmr_list = list()
    player_mmr_list = list()
    teamless_player_list = list()
    # Datastructures that will be used.
    with open(playerfile) as infile:
        reader = csv.reader(infile, delimiter=';')
        for line in reader:
            if line[4] == 'True':
                # Checks if the player is on 'Active'.
                players.append(line[:4])
        for player in players:
            player[1] = int(player[1])
            if player[3] == 'False':
                # Checks if the player wants to be capt.
                while player[1] in player_dict.keys() or player[1] in \
                        captain_dict.keys():
                    player[1] += 1
                    # This makes sure there are no duplicates in the mmr
                    # list. So that behind every dictionary value is ONE
                    # player, In the future I will fix this so there can be
                    # multiple players behind one MMR-key
                player_dict.update({player[1]: [player[0], player[2]]})
                player_mmr_list.append(player[1])
            else:
                while player[1] in captain_dict.keys() or player[1] in \
                        player_dict.keys():
                    player[1] += 1
                    # Ditto.
                captain_dict.update({player[1]: [player[0], player[2]]})
                captain_mmr_list.append(player[1])
    team_amount = len(players) // 5
    while len(captain_mmr_list) < team_amount:
        # If there are not enough captain it will take the highest MMR
        # players from the playerlist and make them captain.
        captain_mmr_list.append(max(player_mmr_list))
        captain_dict.update(
            {max(player_mmr_list): player_dict[max(player_mmr_list)]})
        del player_dict[max(player_mmr_list)]
        player_mmr_list.remove(max(player_mmr_list))
    while (len(captain_mmr_list)) > team_amount:
        # If there aare ot many captains it will remove the lowest MMR
        # captains and add them to the players.
        player_mmr_list.append(min(captain_mmr_list))
        player_dict.update(
            {min(captain_mmr_list): captain_dict[min(captain_mmr_list)]})
        del captain_dict[min(captain_mmr_list)]
        captain_mmr_list.remove(min(captain_mmr_list))
    while len(player_mmr_list) > team_amount * 4:
        # Takes the number of players mod 5 with lowest players being taken
        # out of the pool.
        teamless_player_list.append(player_dict[min(player_mmr_list)][0])
        del player_dict[min(player_mmr_list)]
        player_mmr_list.remove(min(player_mmr_list))
    player_mmr_list = sorted(player_mmr_list, reverse=True)
    captain_mmr_list = sorted(captain_mmr_list, reverse=True)
    # From high to low MMR
    return player_dict, captain_dict, player_mmr_list, captain_mmr_list, \
        team_amount, teamless_player_list


def create_team_dictionaries(team_amount):
    """
    Creates the empty teams in dictionary format.
    Playercount removed at the end of main.
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
    mmr players to get their preffered roles. Low mmr players who want to
    play 4 or 5 will get priority for those roles. Probably gonna add
    functionality for role preference order. Now it just goes through the
    roles from 1 to 5 starting going from high mmr to low mmr players.
    :return: Player and captain list
    with everyone updated to their new role.
    """
    players_on_pref_role = team_amount * 5
    # This value tracks the amount of players that end up on their preffered
    #  role. Any players will count as 'on preffered role'.
    role_amounts = list()
    # This will be used to check how many players of each role there are.
    any_role_captain_mmr_list = list()
    any_role_player_mmr_list = list()
    player_mmr_list_workcopy = sorted(player_mmr_list)
    # The full player_mmr_list will be used lateron in the programm.
    for i in range(6):
        role_amounts.append(0)
        # 6 entries so that the role matches the index in the list.
    cml_itercopy = captain_mmr_list.copy()
    for mmr in cml_itercopy:
        if captain_dict[mmr][1] == 'Any':
            any_role_captain_mmr_list.append(mmr)
            captain_mmr_list.remove(mmr)
            # Adds captains who have role on 'Any' to a seperate list and
            # removed form the normal mmr_list as they will be assigned a
            # role after everyone else.
    pmlwc_itercopy = player_mmr_list_workcopy.copy()
    for mmr in pmlwc_itercopy:
        if player_dict[mmr][1] == 'Any':
            any_role_player_mmr_list.append(mmr)
            player_mmr_list_workcopy.remove(mmr)
            # Ditto but then for non-captain players.
    for mmrlist in [cml_itercopy, player_mmr_list_workcopy]:
        # This loop while assign the support roles to the lowest MMR players
        # with said role on prefference.
        mmrlist_itercopy = mmrlist.copy()
        for role in [5, 4]:
            while role_amounts[role] < team_amount:
                for mmr in mmrlist_itercopy:
                    if mmrlist == captain_mmr_list:
                        if int(captain_dict[mmr][1]) == role:
                            role_amounts[role] += 1
                            mmrlist.remove(mmr)
                    if mmrlist == player_mmr_list_workcopy:
                        if int(player_dict[mmr][1]) == role:
                            role_amounts[role] += 1
                            mmrlist.remove(mmr)
                break
    player_mmr_list_workcopy = sorted(player_mmr_list_workcopy, reverse=True)
    # Now we will go through the players from HIGH to LOW mmr so that the
    # highest MMR players get priority over their preffered roles. (Except
    # the low mmr players that want support, those have been assigned earlier.
    for mmr in captain_mmr_list:
        # Captains will get priority for their role assignment.
        cur_role = int(captain_dict[mmr][1])
        # The role the player wants.
        if role_amounts[cur_role] < team_amount:
            role_amounts[cur_role] += 1
        else:
            for role in enumerate(role_amounts):
                # This means the role the player wanted is no longer
                # available and this loop goes through the roles from 1->5
                # to see which one is still available.
                if role[0] == 0:
                    continue
                elif role[1] < team_amount:
                    role_amounts[role[0]] += 1
                    # This role is still available and will be assigned to
                    # the player. Updating it in his entry in the
                    # dictionary. The tracker for players on their preffered
                    # role will be deducted one point.
                    captain_dict.update({mmr: [captain_dict[mmr][0],
                        str(role[0])]})
                    players_on_pref_role -= 1
                    break
    for mmr in player_mmr_list_workcopy:
        # This is the same as the previous loop but then for the players.
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
    # Now players with 'Any' will be assigned their roles. Priority High to
    # low MMR, 1->5, Captains then Players.
    for mmr in any_role_captain_mmr_list:
        for role in enumerate(role_amounts):
            if role[0] == 0:
                continue
            elif role[1] < team_amount:
                role_amounts[role[0]] += 1
                captain_dict.update({mmr: [captain_dict[mmr][0], str(role[
                    0])]})
                captain_mmr_list.append(mmr)
                break
    for mmr in any_role_player_mmr_list:
        for role in enumerate(role_amounts):
            if role[0] == 0:
                continue
            elif role[1] < team_amount:
                role_amounts[role[0]] += 1
                player_dict.update({mmr: [player_dict[mmr][0], str(role[
                    0])]})
                player_mmr_list.append(mmr)
                break
    return players_on_pref_role


def distribute_captain(captain_dict, captain_mmr_list, teamlist):
    """
    distributes the captains amongst the teams.
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
    :param current_player_index: This is the index of the player in the
    player_list that is currently being considered.
    :return teamlist with one player added:
    """
    if current_player_index is None:
        current_player_index = 0
    current_player = player_dict[player_mmr_list[current_player_index]]
    min_team_avg = None
    min_team_avg_index = None
    # Variables that will hold the lowest avg MMR in the current teamlist
    # and that teams position in the teamlist,
    # with the amounts of players matching the current round of players
    # being distributed.
    for team in teamlist:
        # Looks for the team with the lowest average MMR.
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
        # Looks if that team has a player on the role that the highest MMR
        # player fills. If not, adds him to the team. If so, calls function
        # recursively now looking at the second highest mmr players.
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


def __main__(playerfile):
    """
    pd = player dictionary
    cd = captain dictionary
    pml = player_mmr_list
    cml = captain_mmr_list
    ta = amount of teams
    tlpl = teamless_player_list
    players_on_prefer_role = amount of players that got their primary role.
    :param playerfile:
    :return:
    """
    pd, cd, pml, cml, ta, tlpl = create_player_dicts(playerfile)
    total_players = ta * 5
    tl = create_team_dictionaries(ta)
    players_on_pref_role = distribute_roles(pd, cd, pml, cml, ta)
    distribute_captain(cd, cml, tl)
    for i in range(4):
        for cr in range(ta):
            add_player(pd, pml, tl, i + 1)
    minimum_avg = None
    maximum_avg = None
    for team in tl:
        # Cleans up the team data structure and looks for the team with the
        # highest and lowest average MMR.
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

try:
    if sys.argv[1] == 'versioninfo':
        print('\nDotaTeamMaker_LowSupp')
        print('Written by Jonathan \'Fusion\' Driessen')
        print('Current version: 0.1')
        print('Last updated on 12/01/2018')
    else:
        __main__(sys.argv[1])
except:
    print('\nInput error')
    print('Correct commandline input is:')
    print('python <name of DotaTeamMaker> <Input data>')
