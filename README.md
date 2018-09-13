# KayzrTeamSort
Program used for sorting players into teams for Dota 2 tournaments. Used in the (Kayzr) playerdraft-bot. 

https://github.com/stephanblom/benedota-playerdraft-bot

Current versions:

  * DotaTeamMaker_LowSupp_Weighted (Currently used in bot):
    * Naïve sorting algorithm with pretty good results.
    * Players get appointed custom MMR' based on their real MMR and the impact of the role they are playing.
    * Current weights: {1: 1.3, 2: 1.3, 3: 1, 4: 0.70, 5: 0.70}

  * DotaTeamMaker_BestSolution:
    * Best solution algorithm. But not yet calculable in workable time.
    * Finds best possible solution for the role distribution. (Not yet team distribution.)
    * Also with Weighted MMR

Deprecated Versions:

  * DotaTeamMaker_LowSupp (You can just replicate this by setting the weights to 1 in LowSupp_weighted.)
    * Same as DotaTeamMaker, only this gives low MMR players priority over support roles.

  * DotaTeamMaker: (pre-rewrite 14/01/2018)
    * Distributes roles amongst players first. With priority from High to low MMR. Pos 1 to 5.
    * Only takes into account MMR at the time of player distribution

  * DotaTeamMaker_LowSupp: (pre-rewrite 14/01/2018)
    * Same as DotaTeamMaker, only this gives low MMR players priority over support roles.
