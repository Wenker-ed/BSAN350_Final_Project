# NBA analytics Project

# Classes: BoxScore, TeamStats, Team
# Features: possession estimates, offensive/defensive/net rating, Dean Oliver’s Four Factors, plots, and team comparisons

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import teamgamelog


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
        self._check_consistency()

    def _check_consistency(self):
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


# class Lineup:
#     def __init__(self, players):
#         self.players = players

#     def calculate_efficiency(self, possessions):
#         # Simple efficiency calculation: points per possession
#         return possessions.points_scored / possessions.possessions() if possessions.possessions() > 0 else 0

# TeamStats assumes that BoxScore objects are provided for both the team and the opponent.
class TeamStats:
    def __init__(self, team, team_box_score, opp_box_score):
        self.team = team
        self.box_score = team_box_score
        self.opp_box_score = opp_box_score
        # average the two box scores' possessions
        self.possessions = (team_box_score.possessions() +
                            opp_box_score.possessions()) / 2

    def offensive_rating(self):
        return 100 * (self.box_score.points_scored / self.possessions) if self.possessions > 0 else 0

    def defensive_rating(self):
        return 100 * (self.opp_box_score.points_scored / self.possessions) if self.possessions > 0 else 0

    def net_rating(self):
        return self.offensive_rating() - self.defensive_rating()

    def four_factors(self):
        """Dean Oliver's Four Factors: eFG%, TOV%, ORB%, and FT%

        eFG% = (FGM + 0.5 * 3PM) / FGA

        TOV% = TOV / (FGA + 0.44 * FTA + TOV)

        ORB% = OREB / (OREB + opponent DREB)

        FT% = FTM / FGA

        Returns:
            tuple: A tuple containing the four factors (eFG%, TOV%, ORB%, FT%) as floats rounded to 4 decimal places.
        """

        eFG_percentage = round(((self.box_score.field_goals_made + 0.5 * self.box_score.three_point_made)
                               / self.box_score.field_goals_attempted) * 100, 4) \
            if self.box_score.field_goals_attempted > 0 \
            else 0  # eFG% approximation
        TOV_percentage = round((self.box_score.turnovers /
                               (self.box_score.field_goals_attempted + 0.44 * self.box_score.free_throws_attempted + self.box_score.turnovers)) * 100, 4) \
            if (self.box_score.field_goals_attempted + 0.44 * self.box_score.free_throws_attempted + self.box_score.turnovers) > 0 \
            else 0  # TOV%
        ORB_percentage = round((self.box_score.offensive_rebounds /
                               (self.box_score.offensive_rebounds + self.opp_box_score.defensive_rebounds)) * 100, 4) \
            if (self.box_score.offensive_rebounds + self.opp_box_score.defensive_rebounds) > 0 \
            else 0  # ORB%
        FT_percentage = round((self.box_score.free_throws_made / self.box_score.field_goals_attempted) * 100, 4) \
            if self.box_score.field_goals_attempted > 0 \
            else 0  # FT%

        print(
            f"Oliver's Four Factors for the {self.team}:\
            \neFG%: {eFG_percentage}, \
            \nTOV%: {TOV_percentage},\
            \nORB%: {ORB_percentage},\
            \nFT%: {FT_percentage}"
        )

        return eFG_percentage, TOV_percentage, ORB_percentage, FT_percentage


class Team(TeamStats):
    def __init__(self, full_name, season):
        self.id = teams.find_teams_by_full_name(full_name)[0]['id']
        self.name = full_name
        self.games = []
        self.season = season
        self._load_games()

    def add_game(self, box_score):
        self.games.append(box_score)

    def _load_games(self):

        try:
            gamelog = teamgamelog.TeamGameLog(
                team_id=self.id,
                season=self.season
            )

            df = gamelog.get_data_frames()[0]

            if df.empty:
                raise ValueError(
                    f"No game data found for {self.name} in {self.season}"
                )

            self.games.clear()

            for _, row in df.iterrows():

                # We don't have opponent points from TeamGameLog
                # so use a placeholder for now

                game = BoxScore(
                    team=self.name,
                    # gets the opponents abbreviation from the matchup string
                    opponent=row["MATCHUP"].split()[-1],
                    points_scored=row["PTS"],
                    points_allowed=0,
                    field_goals_attempted=row["FGA"],
                    field_goals_made=row["FGM"],
                    three_point_attempted=row["FG3A"],
                    three_point_made=row["FG3M"],
                    free_throws_attempted=row["FTA"],
                    free_throws_made=row["FTM"],
                    turnovers=row["TOV"],
                    offensive_rebounds=row["OREB"],
                    defensive_rebounds=row["DREB"]
                )

                game.game_id = row["Game_ID"]

                self.add_game(game)

            print(f"Loaded {len(self.games)} games for {self.name}")

        except ValueError as e:
            print(f"Data Error: {e}")

        except IndexError:
            print("Unexpected API response format.")

        except Exception as e:
            print(f"Error loading games: {e}")

    def plot_four_factors(self):
        import matplotlib.pyplot as plt
        four_factors = self.four_factors()
        labels = ['eFG%', 'TOV%', 'ORB%', 'FT%']
        values = [four_factors['eFG%'], four_factors['TOV%'],
                  four_factors['ORB%'], four_factors['FT%']]
        plt.bar(labels, values)
        plt.title(f"Four Factors for {self.name}")
        plt.show()

    def plot_net_rating(self):
        import matplotlib.pyplot as plt
        plt.bar(['Offensive', 'Defensive', 'Net'], [
                self.offensive_rating(), self.defensive_rating(), self.net_rating()])
        plt.title(f"Ratings for {self.name}")
        plt.show()

    def compare(self, other_team):
        print(f"Comparing {self.name} vs {other_team.name}")
        print(f"Net Rating: {self.net_rating()} vs {other_team.net_rating()}")
        print(
            f"Four Factors: {self.four_factors()} vs {other_team.four_factors()}")
