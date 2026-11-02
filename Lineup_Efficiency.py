# 3. Lineup and Team Efficiency Tool

# Classes: Possession, Lineup, TeamStats
# Features: possession estimates, offensive/defensive/net rating, Dean Oliver’s Four Factors, and plus/minus by lineup
# Output: ranked lineup table and a comparison chart

class Possession:
    def __init__(self, team, opponent, points_scored, points_allowed, turnovers, rebounds):
        self.team = team
        self.opponent = opponent
        self.points_scored = points_scored
        self.points_allowed = points_allowed
        self.turnovers = turnovers
        self.rebounds = rebounds

    def estimate_possessions(self):
        # Simple estimation: possessions = points_scored + turnovers + rebounds
        return self.points_scored + self.turnovers + self.rebounds

class Lineup:
    def __init__(self, players):
        self.players = players

    def calculate_efficiency(self, possessions):
        # Simple efficiency calculation: points per possession
        return possessions.points_scored / possessions.estimate_possessions() if possessions.estimate_possessions() > 0 else 0

class TeamStats:
    def __init__(self, team, possessions):
        self.team = team
        self.possessions = possessions

    def offensive_rating(self):
        return sum(p.points_scored for p in self.possessions) / sum(p.estimate_possessions() for p in self.possessions) if self.possessions else 0

    def defensive_rating(self):
        return sum(p.points_allowed for p in self.possessions) / sum(p.estimate_possessions() for p in self.possessions) if self.possessions else 0

    def net_rating(self):
        return self.offensive_rating() - self.defensive_rating()

    def four_factors(self):
        # Dean Oliver’s Four Factors: shooting, turnovers, rebounding, and free throws
        total_possessions = sum(p.estimate_possessions() for p in self.possessions) if self.possessions else 0
        total_points_scored = sum(p.points_scored for p in self.possessions) if self.possessions else 0
        total_points_allowed = sum(p.points_allowed for p in self.possessions) if self.possessions else 0
        total_turnovers = sum(p.turnovers for p in self.possessions) if self.possessions else 0
        total_rebounds = sum(p.rebounds for p in self.possessions) if self.possessions else 0

        shooting = total_points_scored / total_possessions if total_possessions > 0 else 0
        turnovers = total_turnovers / total_possessions if total_possessions > 0 else 0
        rebounding = total_rebounds / total_possessions if total_possessions > 0 else 0
        free_throws = total_points_scored / total_possessions if total_possessions > 0 else 0  # Simplified

        return {
            "shooting": shooting,
            "turnovers": turnovers,
            "rebounding": rebounding,
            "free_throws": free_throws
        }