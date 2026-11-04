# 3. Lineup and Team Efficiency Tool

# Classes: Possession, Lineup, TeamStats
# Features: possession estimates, offensive/defensive/net rating, Dean Oliver’s Four Factors, and plus/minus by lineup
# Output: ranked lineup table and a comparison chart

class BoxScore:
    def __init__(self, team, opponent, points_scored=0, points_allowed=0, field_goals_attempted=0, field_goals_made=0,
                 three_point_attempted=0, three_point_made=0, free_throws_attempted=0, free_throws_made=0,
                 turnovers=0, offensive_rebounds=0, defensive_rebounds=0
                 ):
        self.team = team
        self.opponent = opponent
        self.points_scored = points_scored
        self.points_allowed = points_allowed
        self.field_goals_attempted = field_goals_attempted
        self.field_goals_made = field_goals_made
        self.three_point_attempted = three_point_attempted
        self.three_point_made = three_point_made
        self.free_throws_attempted = free_throws_attempted
        self.free_throws_made = free_throws_made
        self.turnovers = turnovers
        self.offensive_rebounds = offensive_rebounds
        self.defensive_rebounds = defensive_rebounds
        self.check_consistency()

    def check_consistency(self):
        """Check the consistency of the box score data.

        Raises:
            Exception: If any of the box score values are inconsistent.
        """

        if self.points_scored < 0 or self.points_allowed < 0:
            raise Exception("Points cannot be negative.")
        if self.field_goals_made > self.field_goals_attempted:
            raise Exception("fgm cannot exceed fga.")
        if self.three_point_attempted > self.field_goals_attempted:
            raise Exception("3pa cannot exceed fga.")
        if self.three_point_made > self.field_goals_made:
            raise Exception("3pm cannot exceed fgm.")
        if self.free_throws_made > self.free_throws_attempted:
            raise Exception("ftm cannot exceed fta.")
        if self.turnovers < 0:
            raise Exception("Turnovers cannot be negative.")
        if self.offensive_rebounds < 0:
            raise Exception("Offensive rebounds cannot be negative.")
        if self.defensive_rebounds < 0:
            raise Exception("Defensive rebounds cannot be negative.")
        if self.free_throws_attempted < 0:
            raise Exception("Free throws attempted cannot be negative.")
        if self.free_throws_made < 0:
            raise Exception("Free throws made cannot be negative.")
        if self.field_goals_attempted < 0:
            raise Exception("Field goals attempted cannot be negative.")
        if self.field_goals_made < 0:
            raise Exception("Field goals made cannot be negative.")
        if self.three_point_attempted < 0:
            raise Exception("Three-point attempts cannot be negative.")
        if self.three_point_made < 0:
            raise Exception("Three-point made cannot be negative.")

    def possessions(self):
        """Possessions (POSS) ≈ FGA - ORB + TOV + 0.44 * FTA 
        www.socialsporthub.com

        Where:

        FGA = Field Goals Attempted

        FTA = Free Throws Attempted
        
        ORB = Offensive Rebounds
        
        TOV = Turnovers
        
        The 0.44 coefficient is Oliver's empirical estimate that about 44% of free throws end a possession 
        (the rest are “and-one” situations, bonus fouls, or other non-possession-ending free throws)

        Returns: 
            Estimated number of possessions for the given box score.
        """
        # return self.field_goals_attempted - self.offensive_rebounds + self.turnovers + 0.44 * self.free_throws_attempted        
        return self.field_goals_attempted - self.offensive_rebounds + self.turnovers + 0.44 * self.free_throws_attempted


class Lineup:
    def __init__(self, players):
        self.players = players

    def calculate_efficiency(self, possessions):
        # Simple efficiency calculation: points per possession
        return possessions.points_scored / possessions.possessions() if possessions.possessions() > 0 else 0

class TeamStats:
    def __init__(self, team, team_box_score, opp_box_score):
        self.team = team
        self.box_score = team_box_score
        self.opp_box_score = opp_box_score
        self.possessions = team_box_score.possessions()

    def offensive_rating(self):
        return self.box_score.points_scored / self.possessions if self.possessions > 0 else 0

    def defensive_rating(self):
        return self.opp_box_score.points_scored / self.possessions if self.possessions > 0 else 0

    def net_rating(self):
        return self.offensive_rating() - self.defensive_rating()

    def four_factors(self):
        """Dean Oliver's Four Factors: eFG%, TOV%, ORB%, and FT%

        eFG% = (FGM + 0.5 * 3PM) / FGA

        TOV% = TOV / (FGA + 0.44 * FTA + TOV)

        ORB% = OREB / (OREB + opponent DREB)

        FT% = FTM / FGA
        """

        eFG_percentage = (self.box_score.field_goals_made + 0.5 * self.box_score.three_point_made) / self.box_score.field_goals_attempted if self.box_score.field_goals_attempted > 0 else 0  # eFG% approximation
        TOV_percentage = self.box_score.turnovers / (self.possessions + self.box_score.offensive_rebounds) if (self.possessions + self.box_score.offensive_rebounds) > 0 else 0  # TOV%
        ORB_percentage = self.box_score.offensive_rebounds / (self.box_score.offensive_rebounds + self.opp_box_score.defensive_rebounds) if (self.box_score.offensive_rebounds + self.opp_box_score.defensive_rebounds) > 0 else 0  # ORB%
        FT_percentage = self.box_score.free_throws_made / self.box_score.free_throws_attempted if self.box_score.free_throws_attempted > 0 else 0  # FT%
        # ORB_percentage = self.box_score.offensive_rebounds / (self.box_score.offensive_rebounds + total_defensive_rebounds) if (self.box_score.offensive_rebounds + total_defensive_rebounds) > 0 else 0
        # free_throws = self.box_score.free_throws_made / self.box_score.free_throws_attempted if self.box_score.free_throws_attempted > 0 else 0  # Simplified
        print(f"Oliver's Four Factors for the {self.team}:\neFG%: {eFG_percentage}, \nTOV%: {TOV_percentage},\nORB%: {ORB_percentage}, \nFT%: {FT_percentage}")

        return eFG_percentage, TOV_percentage, ORB_percentage, FT_percentage