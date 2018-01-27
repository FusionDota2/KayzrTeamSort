# KayzrTeamSort
Program used for sorting players into teams for Dota 2 tournaments.

Current versions:

  * DotaTeamMaker_Normal:
    * Distributes roles amongst players first. With priority from High to low MMR. Pos 1 to 5.
    * Only takes into account MMR at the time of player distribution
    * Possible input includes Multiple roles in order of wanting and 'Any'.

  * DotaTeamMaker_LowSupp
    * Same as DotaTeamMaker, only this gives low MMR players priority over support roles.

  * DotaTeamMaker_LowSupp_Weighted:
    * Same sorting algorithm as DotaTeamMaker_LowSupp.
    * Players get appointed custom MMR' based on their real MMR and the impact of the role they are playing.
    * Current weights: {1: 1.25, 2: 1.25, 3: 1, 4: 0.75, 5: 0.75}

Depricated Versions:

  * DotaTeamMaker: (pre-rewrite 14/01/2018)
    * Distributes roles amongst players first. With priority from High to low MMR. Pos 1 to 5.
    * Only takes into account MMR at the time of player distribution

  * DotaTeamMaker_LowSupp: (pre-rewrite 14/01/2018)
    * Same as DotaTeamMaker, only this gives low MMR players priority over support roles.
