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

import csv
import sys
from os.path import isfile

POSSIBLE_ROLES = [1, 2, 3, 4, 5]


class Player(object):
    # Didn't put in getters and setters because I'm not sure yet
    # Where I want to go with this program.
    players_off_role = 0

    def __init__(self, name, mmr, captain_pref, roles):
        self.name = name

        try:
            self.real_mmr = int(mmr)
        except:
            sys.exit('MMR has to be a number. Not ' + mmr)

        self.mmr = None

        role_list = list()
        for role in roles:
            if role == 'Any' or int(role) in POSSIBLE_ROLES:
                if role == 'Any':
                    role_list.append('Any')
                else:
                    role_list.append(int(role))
            else:
                sys.exit('Role has to be a number between 1 and 5 or '
                         '\'Any\'. Not ' + str(role))
        self.role_preference = role_list
        self.role = None

        if captain_pref == 'True' or captain_pref == 'False':
            if captain_pref == 'True':
                captain_pref = True
            elif captain_pref == 'False':
                captain_pref = False
        else:
            sys.exit('The captain field has to be True or '
                     'False. Not ' + str(captain_pref))
        self.captain_preference = captain_pref

        self.active_captain = False

    def __str__(self):
        return '%s: MMR = %s, role_pref = %s, role = %s, captainpref = %s, ' \
               'captainstatus = %s' % (self.name, self.real_mmr,
        self.role_preference, self.role, self.captain_preference,
        self.active_captain)

    def calc_mmr(self):
        self.mmr = self.real_mmr


class Team(object):
    def __init__(self):
        self.playerlist = list()
        for i in range(6):
            self.playerlist.append(None)
        self.average = 0
        self.playercount = 0
        self.captain = None
        self.team = {1: None, 2: None, 3: None, 4: None, 5: None, 'Captain':
            None, 'Avg': 0, 'Playercount': 0}

    def __str__(self):
        return str(self.team)

    def update_average(self):
        total = 0
        for entry in self.playerlist:
            if isinstance(entry, Player):
                total += entry.mmr
        self.average = float(total / self.playercount)
        self.team['Avg'] = self.average

    def add_player(self, player):
        if isinstance(player, Player):
            self.playerlist[player.role] = player
            self.team[player.role] = player.name
            self.playercount += 1
            self.team['Playercount'] += 1
            self.update_average()
        else:
            print('You tried to add a non-player object')

    def set_captain(self, captain):
        self.captain = captain
        self.team['Captain'] = captain.name


def create_players(playerfile):
    """
    Creates the Players objects and makes a list cotaining those objects.
    :return: Playerlist
    """
    players = list()
    with open(playerfile) as infile:
        reader = csv.reader(infile, delimiter=';')
        for line in reader:
            players.append(Player(line[0], line[1], line[2], line[3:]))
    team_amount = len(players) // 5
    players = sorted(players, key=lambda x: x.real_mmr, reverse=True)
    teamless_players = players[team_amount * 5:]
    players = players[:team_amount * 5]
    return players, teamless_players, team_amount


def update_captain_status(players, team_amount):
    captains = list()
    remove_list = list()
    for player in players:
        if player.captain_preference is True:
            player.active_captain = True
            captains.append(player)
            remove_list.append(player)
        if len(captains) >= team_amount:
            break
    for player in remove_list:
        players.remove(player)
    while len(captains) < team_amount:
        players[0].active_captain = True
        captains.append(players[0])
        players.remove(players[0])
    return players, captains


def create_teams(team_amount):
    teams = list()
    for i in range(team_amount):
        teams.append(Team())
    return teams


def distribute_roles(players, captains, team_amount):
    role_amounts = list()
    everyone = list()
    for player in players:
        everyone.append(player)
    for captain in captains:
        everyone.append(captain)
    everyone.sort(key=lambda x: x.real_mmr)
    # This will be used to check how many players of each role there are.
    for i in range(6):
        role_amounts.append(0)
    # 6 entries so that the role matches the index in the list.
    # This is just QOL.
    for person in everyone:
        if person.role is None:
            for role in person.role_preference:
                if role == 'Any':
                    break
                else:
                    if role_amounts[role] < team_amount:
                        person.role = role
                        role_amounts[role] += 1
                        person.calc_mmr()
                        break
                        # If the role the person wants is avalable he will
                        # receieve it and the role_amounts will be updated.
        if person.role is None and 'Any' not in person.role_preference:
            Player.players_off_role += 1
            # If the role the capatin wants is taken, he will
            # Get one assigned later with the 'Any' play/capt
    # These next 2 loops distribute the remaining free roles amongst the
    # captains and players. Priorty: High->Low MMR,Position 1 -> Position 5
    everyone.sort(key=lambda x: x.real_mmr, reverse=True)
    for person in everyone:
        if person.role is None:
            for role_and_amount in enumerate(role_amounts):
                # role_and_amount will return tuples with first value
                # being the role, the second value the amount of players
                # already on that role.
                if role_and_amount[0] == 0:
                    continue
                elif role_and_amount[1] < team_amount:
                    role_amounts[role_and_amount[0]] += 1
                    person.role = role_and_amount[0]
                    person.calc_mmr()
                    break
    players = sorted(players, key=lambda x: x.mmr, reverse=True)
    captains = sorted(captains, key=lambda x: x.mmr, reverse=True)
    return players, captains


def distribute_captains(captains, teams):
    for i in range(len(captains)):
        teams[i].add_player(captains[i])
        teams[i].set_captain(captains[i])


def distribute_player(players, teams, cur_round, current_index=None):
    """
    Takes the highest MMR player yet to be distributed and tries to add them
    to the team with the lowest MMR average. (With the right amount of players
    for that round of player distributions. If that spot is not yet filled
    the player is added to the team. Else this function is called recursively
    now consindering the second highest MMR player yet to be distributed.
    """
    if current_index is None:
        current_index = 0
    current_player = players[current_index]
    # Variables that will hold the lowest avg MMR in the current teamlist
    # with the amount of players matching the current round of players
    # being distributed.
    templist = list()
    for team in teams:
        if team.playercount == cur_round:
            templist.append(team)
    min_team_avg = min([l.average for l in templist])
    min_avg_team = None
    # Fucking IDE is crying so i have to put in this last line.
    for team in templist:
        if team.average == min_team_avg:
            min_avg_team = team
    if min_avg_team.team[current_player.role] is None:
        # Looks if that team has a player on the role that the highest MMR
        # player fills. If not, adds him to the team. If so, calls function
        # recursively now looking at the second highest mmr players.
        min_avg_team.add_player(current_player)
        players.remove(current_player)
        return None
    else:
        return distribute_player(players, teams, cur_round, current_index + 1)


def write_away(teams, max_spread, role_frac, teamless_player_list, outfile):
    """
    Writes the team data to a csv file (one is created if it doesn't exist
    yet) that includes the teamlist, max mmr spread and the fraction of
    players playing their preffered role.
    """
    with open(outfile, mode='w+') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow([
            'There is a maximum spread of %.1f on the team MMR\'rs' %
            max_spread])
        writer.writerow(
            [role_frac + ' People are playing their preffered roles'])
        i = 0
        for team in teams:
            i += 1
            writelist = list()
            writer.writerow(['Team ' + str(i)])
            for key in team.team.keys():
                writelist.append(str(key) + ':' + str(team.team[key]))
            writer.writerow(writelist)
        writer.writerow(['Players without a team:'])
        writer.writerow(teamless_player_list)


def __main__(playerfile, outfile='Outfile.csv'):
    players, teamless_players, team_amount = create_players(playerfile)
    total_players = team_amount * 5
    players, captains = update_captain_status(players, team_amount)
    teams = create_teams(team_amount)
    players, captains = distribute_roles(players, captains, team_amount)
    distribute_captains(captains, teams)
    players_worklist = players.copy()
    for cur_round in range(1, 5):
        for i in range(team_amount):
            distribute_player(players_worklist, teams, cur_round)
    minimum_avg = min([l.average for l in teams])
    maximum_avg = max([l.average for l in teams])
    for team in teams:
        del team.team['Playercount']
    maximum_spread = maximum_avg - minimum_avg
    players_on_role_frac = str(team_amount * 5 - Player.players_off_role) + \
                           '/' + str(total_players)
    teamless_players_out = list()
    for player in teamless_players:
        teamless_players_out.append(player.name)
    write_away(teams, maximum_spread, players_on_role_frac,
               teamless_players_out, outfile)


if len(sys.argv) == 1:
    sys.argv.append('versioninfo')
if sys.argv[1] == 'versioninfo':
    print('\nDotaTeamMaker_Normal')
    print('Written by Jonathan \'Fusion\' Driessen')
    print('Current version: 1.1.c')
    print('Last updated on 28/01/2018')
elif len(sys.argv) == 2:
    try:
        __main__(sys.argv[1])
    except FileNotFoundError:
        print('\nInput error')
        print('Input file doesn\'t exist')
        print('Correct commandline input is:')
        print('python <name of DotaTeamMaker> <Input data> <Optional: '
              'Outfile name>')
    except:
        raise
elif len(sys.argv) == 3:
    if not sys.argv[2].endswith('.csv'):
        print('\nInput error')
        print('Output file is not a .csv file')
        print('Correct commandline input is:')
        print('python <name of DotaTeamMaker> <Input data> <Optional: '
              'Outfile name>')
    try:
        if isfile(sys.argv[2]):
            print('This file will be overwritten: '
                  + str(sys.argv[2]))
            confirmation = input('Are you sure? (y/n)')
            if confirmation == 'y':
                __main__(sys.argv[1], sys.argv[2])
            else:
                print('Canceled.')
        else:
            __main__(sys.argv[1], sys.argv[2])
    except FileNotFoundError:
        print('\nInput error')
        print('Input file doesn\'t exist')
        print('Correct commandline input is:')
        print('python <name of DotaTeamMaker> <Input data> <Optional: '
              'Outfile name>')
    except:
        raise
