# NBA analytics Project

# Classes: BoxScore, GameStats, Team
# Features: possession estimates, offensive/defensive/net rating, Dean Oliver’s Four Factors, plots, and team comparisons

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import teamgamelog
import matplotlib.pyplot as plt
import numpy as np


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
class GameStats:
    def __init__(self, team_name, team_box_score, opp_box_score):
        self.team_name = team_name
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
            f"Oliver's Four Factors for the {self.team_name}:\
            \neFG%: {eFG_percentage}, \
            \nTOV%: {TOV_percentage},\
            \nORB%: {ORB_percentage},\
            \nFT%: {FT_percentage}"
        )

        return eFG_percentage, TOV_percentage, ORB_percentage, FT_percentage

    def plot_four_factors(self):
        efg, tov, orb, ft = self.four_factors()
        labels = ['eFG%', 'TOV%', 'ORB%', 'FT%']
        values = [efg, tov, orb, ft]
        plt.bar(labels, values)
        plt.title(f"Four Factors for {self.team_name}")
        plt.show()

    def plot_net_rating(self):
        plt.bar(['Offensive', 'Defensive', 'Net'], [
                self.offensive_rating(), self.defensive_rating(), self.net_rating()])
        plt.title(f"Ratings for {self.team_name}")
        plt.show()

    def compare(self, other_team):
        print(f"Comparing {self.team_name} vs {other_team.team_name}")
        print(f"Net Rating: {self.net_rating()} vs {other_team.net_rating()}")
        print(
            f"Four Factors: {self.four_factors()} vs {other_team.four_factors()}")
        return None


class SeasonStats(GameStats):
    def __init__(self, team):
        self.team = team

    def get_team_name(self):
        return self.team.team_name

    def get_team_id(self):
        return self.team.id

    def get_season(self):
        return self.team.season

    def total_points(self):
        return sum(game.points_scored for game in self.team.games)

    def total_points_allowed(self):
        return sum(game.opponent.points_scored for game in self.team.opponent.games)

    def total_possessions(self):
        return sum(game.estimated_possessions for game in self.team.games)

    def season_offensive_rating(self):
        return 100 * (self.total_points() / self.total_possessions() if self.total_possessions() > 0 else 0)

    def season_defensive_rating(self):
        return 100 * (self.total_points_allowed() / self.total_possessions() if self.total_possessions() > 0 else 0)

    def season_net_rating(self):
        return self.season_offensive_rating() - self.season_defensive_rating()

    def season_four_factors(self):
        """Dean Oliver's Four Factors: eFG%, TOV%, ORB%, and FT%

        eFG% = (FGM + 0.5 * 3PM) / FGA

        TOV% = TOV / (FGA + 0.44 * FTA + TOV)

        ORB% = OREB / (OREB + opponent DREB)

        FT% = FTM / FGA

        Returns:
            tuple: A tuple containing the four factors (eFG%, TOV%, ORB%, FT%) as floats rounded to 4 decimal places.
        """
        fga = sum(game.field_goals_attempted for game in self.team.games)
        fgm = sum(game.field_goals_made for game in self.team.games)
        three_pm = sum(game.three_point_made for game in self.team.games)
        tov = sum(game.turnovers for game in self.team.games)
        fta = sum(game.free_throws_attempted for game in self.team.games)
        ftm = sum(game.free_throws_made for game in self.team.games)
        oreb = sum(game.offensive_rebounds for game in self.team.games)
        opp_dreb = sum(
            game.defensive_rebounds for game in self.team.opponent.games)

        eFG_percentage = round(((fgm + 0.5 * three_pm) / fga) * 100, 4) \
            if fga > 0 \
            else 0  # eFG% approximation
        TOV_percentage = round((tov / (fga + 0.44 * fta + tov)) * 100, 4) \
            if (fga + 0.44 * fta + tov) > 0 \
            else 0  # TOV%
        ORB_percentage = round((oreb / (oreb + opp_dreb)) * 100, 4) \
            if (oreb + opp_dreb) > 0 \
            else 0  # ORB%
        FT_percentage = round((ftm / fga) * 100, 4) \
            if fga > 0 \
            else 0  # FT%

        print(
            f"Oliver's Four Factors for the {self.team_name}:\
            \neFG%: {eFG_percentage}, \
            \nTOV%: {TOV_percentage},\
            \nORB%: {ORB_percentage},\
            \nFT%: {FT_percentage}"
        )

        return eFG_percentage, TOV_percentage, ORB_percentage, FT_percentage

    def plot_four_factors(self):
        efg, tov, orb, ft = self.season_four_factors()
        labels = ['eFG%', 'TOV%', 'ORB%', 'FT%']
        values = [efg, tov, orb, ft]
        plt.bar(labels, values)
        plt.title(f"Four Factors for {self.get_team_name()}")
        plt.show()

    def plot_net_rating(self):
        plt.bar(['Offensive', 'Defensive', 'Net'], [
                self.season_offensive_rating(), self.season_defensive_rating(), self.season_net_rating()])
        plt.title(f"Ratings for {self.get_team_name()}")
        plt.show()

    def compare(self, other_team):
        print(f"Comparing {self.get_team_name()} vs {other_team.get_team_name()}")
        print(
            f"Net Rating: {self.season_net_rating()} vs {other_team.season_net_rating()}")
        print(
            f"Four Factors: {self.season_four_factors()} vs {other_team.season_four_factors()}")
        return None


class Team:
    def __init__(self, full_name, season):
        self.id = teams.find_teams_by_full_name(full_name)[0]['id']
        self.team_name = full_name
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
                    f"No game data found for {self.team_name} in {self.season}"
                )

            self.games.clear()

            for _, row in df.iterrows():

                # We don't have opponent points from TeamGameLog
                # so use a placeholder for now

                game = BoxScore(
                    team=self.team_name,
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
                game.estimated_possessions = game.possessions()

                self.add_game(game)

            print(f"Loaded {len(self.games)} games for {self.team_name}")

        except ValueError as e:
            print(f"Data Error: {e}")

        except IndexError:
            print("Unexpected API response format.")

        except Exception as e:
            print(f"Error loading games: {e}")

    def get_game_id(self, opponent_abbreviation):
        """
        Returns the game ID for the game against the specified opponent.
        Returns None if no such game exists.
        """
        for game in self.games:
            if game.opponent == opponent_abbreviation:
                return game.game_id
        return None

    def get_game(self, game_id):
        for game in self.games:
            if game.game_id == game_id:
                return game
        return None

    # def plot_four_factors(self):
    #     four_factors = self.four_factors()
    #     labels = ['eFG%', 'TOV%', 'ORB%', 'FT%']
    #     values = [four_factors['eFG%'], four_factors['TOV%'],
    #               four_factors['ORB%'], four_factors['FT%']]
    #     plt.bar(labels, values)
    #     plt.title(f"Four Factors for {self.name}")
    #     plt.show()
    #     plt.title(f"Four Factors for {self.team_name}")
    #     plt.show()
    #     plt.title(f"Four Factors for {self.name}")
    #     plt.show()

    # def plot_net_rating(self):
    #     plt.bar(['Offenive', 'Defensive', 'Net'], [
    #             self.offensive_rating(), self.defensive_rating(), self.net_rating()])
    #     plt.title(f"Ratings for {self.name}")
    #     plt.show()

    # def compare(self, other_team):
    #     print(f"Comparing {self.name} vs {other_team.name}")
    #     print(f"Net Rating: {self.net_rating()} vs {other_team.net_rating()}")
    #     print(
    #         f"Four Factors: {self.four_factors()} vs {other_team.four_factors()}")
    #     return None


# team_name = "Minnesota Timberwolves"
# my_team = Team(full_name=team_name, season="2026-27")
# opponent_team_name = "San Antonio Spurs"
# opponent_team = Team(full_name=opponent_team_name, season="2026-27")
# my_team_stats = TeamStats(team=my_team, team_box_score=my_team.get_game(my_team.get_game_id(
#     'SAS')), opp_box_score=opponent_team.get_game(opponent_team.get_game_id('MIN')))
# # my_team_stats = TeamStats(team=my_team, team_box_score=my_team.games[],opp_box_score=)
# my_team_stats.plot_net_rating()
# my_team_stats.plot_four_factors()
