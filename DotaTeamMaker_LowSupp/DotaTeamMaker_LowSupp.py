import csv
import sys
from os.path import isfile


class Player(object):
    # Purposely did not use getters and setters for each variable because
    # I'm not sure yet what way I want to go with this program.
    players_off_role = 0

    def __init__(self, name, mmr, role, captain_pref):
        self.name = name
        try:
            self.real_mmr = int(mmr)
        except:
            sys.exit('MMR has to be a number. Not ' + mmr)
        self.mmr = None
        if not role == 'Any' and 5 >= int(role) >= 1:
             self.role_preference = int(role)
        elif role == 'Any':
            self.role_preference = 'Any'
        else:
            sys.exit('Role has to be a number between 1 and 5 or \'Any\'.')
        self.role = None
        if captain_pref == 'True' or captain_pref == 'False' or captain_pref \
                is True or captain_pref is False:
            if captain_pref == 'True':
                captain_pref = True
            elif captain_pref == 'False':
                captain_pref = False
        else:
            sys.exit('The active field has to be True or '
                     'False. Not ' + str(captain_pref))
        self.captain_preference = captain_pref
        self.active_captain = False

    def __str__(self):
        return '%s: MMR = %s, role_pref = %s, role = %s, captainpref = %s, ' \
               'captainstatus = %s' % (self.name, self.real_mmr,
                self.role_preference, self.role,self.captain_preference,
                self.active_captain)


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
                total += entry.real_mmr
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
            if line[4] == 'True':
                # Checks if the player is on 'Active'.
                players.append(Player(line[0], line[1], line[2], line[3]))
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
    # This will be used to check how many players of each role there are.
    for i in range(6):
        role_amounts.append(0)
    # 6 entries so that the role matches the index in the list.
    # This is just QOL.
    for role in [5, 4]:
        for captain in sorted(captains, key=lambda x: x.real_mmr):
            if captain.role_preference == 'Any':
                continue
            if captain.role_preference == role and role_amounts[role]\
                    < team_amount:
                captain.role = role
                role_amounts[role] += 1
    for role in [5, 4]:
        for player in sorted(players, key=lambda x: x.real_mmr):
            if player.role_preference == 'Any':
                continue
            if player.role_preference == role and role_amounts[role]\
                    < team_amount:
                player.role = role
                role_amounts[role] += 1
    for captain in captains:
        # Captains will get priority for their role assignment.
        if captain.role is None:
            if captain.role_preference == 'Any':
                continue
            else:
                if role_amounts[captain.role_preference] < team_amount:
                    captain.role = captain.role_preference
                    role_amounts[captain.role_preference] += 1
                    # If the role the captain wants is avalable he will
                    # receieve it and the role_amounts will be updated.
                else:
                    for role in enumerate(role_amounts):
                        # This means the role the player wanted is no longer
                        # available and this loop goes through the roles
                        # from 1->5 to see which one is still available.
                        if role[0] == 0:
                            break
                        elif role[1] < team_amount:
                            captain.role = role[0]
                            role_amounts[role[0]] += 1
                            Player.players_off_role += 1
                            break
                            # And available role has been found and the
                            # captain will be assigned this role. The loop
                            # will stop and the tracker for players off pref
                            # role is updated.
    for player in players:
        # Same but then for the players.
        if player.role is None:
            if player.role_preference != 'Any':
                if role_amounts[player.role_preference] < team_amount:
                    player.role = player.role_preference
                    role_amounts[player.role_preference] += 1
                else:
                    for role in enumerate(role_amounts):
                        if role[0] == 0:
                            continue
                        elif role[1] < team_amount:
                            player.role = role[0]
                            role_amounts[role[0]] += 1
                            Player.players_off_role += 1
                            break
    # These next 2 loops distribute the remaining free roles amongst the any
    # captains and players. Priorty: Captain -> Player, High MMR -> Low MMR,
    # Position 1 -> Position 5
    for captain in captains:
        if captain.role_preference == 'Any':
            for role in enumerate(role_amounts):
                if role[0] == 0:
                    continue
                elif role[1] < team_amount:
                    role_amounts[role[0]] += 1
                    captain.role = role[0]
                    break
    for player in players:
        if player.role_preference == 'Any':
            for role in enumerate(role_amounts):
                if role[0] == 0:
                    continue
                elif role[1] < team_amount:
                    role_amounts[role[0]] += 1
                    player.role = role[0]
                    break
    for i in [1,2,3,4,5,]:
        som = 0
        for player in players:
            if player.role == i:
                som += 1
        for captain in captains:
            if captain.role == i:
                som += 1
    return None


def distribute_captains(captains, teams):
    for i in range(len(captains)):
        teams[i].add_player(captains[i])
        teams[i].set_captain(captains[i])


def distribute_player(players, teams, cur_round, current_index = None):
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
        writer.writerow(['There is a maximum spread of ' + str(
            max_spread) + ' on the team MMR\'rs'])
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
    total_players = team_amount*5
    players, captains = update_captain_status(players, team_amount)
    teams = create_teams(team_amount)
    distribute_roles(players, captains, team_amount)
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
    players_on_role_frac = str(team_amount*5 - Player.players_off_role) + \
                           '/' + str(total_players)
    teamless_players_out = list()
    for player in teamless_players:
        teamless_players_out.append(player.name)
    write_away(teams, maximum_spread, players_on_role_frac,
               teamless_players_out, outfile)


if len(sys.argv) == 1:
    sys.argv.append('versioninfo')
if sys.argv[1] == 'versioninfo':
    print('\nDotaTeamMaker_LowSupp')
    print('Written by Jonathan \'Fusion\' Driessen')
    print('Current version: 1.0.b')
    print('Last updated on 14/01/2018')
elif not sys.argv[1].endswith('.csv'):
        print('\nInput error')
        print('Input file is not a .csv file')
        print('Correct commandline input is:')
        print('python <name of DotaTeamMaker> <Input data> <Optional: '
              'Outfile name>')
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

