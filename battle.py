from __future__ import annotations
from enum import auto
from typing import Optional

from base_enum import BaseEnum
from team import MonsterTeam


class Battle:
    class Action(BaseEnum):
        ATTACK = auto()
        SWAP = auto()
        SPECIAL = auto()

    class Result(BaseEnum):
        TEAM1 = auto()
        TEAM2 = auto()
        DRAW = auto()

    def __init__(self, verbosity=0) -> None:
        self.verbosity = verbosity

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.
        """
        action1 = self.team1.choose_action(self.out1, self.out2)
        action2 = self.team2.choose_action(self.out2, self.out1)
        if action1 == Battle.Action.SWAP:
            self.team1.add_to_team(self.out1)
            self.out1 = self.team1.retrieve_from_team()
        elif action1 == Battle.Action.SPECIAL:
            self.team1.add_to_team(self.out1)
            self.team1.special()
            self.out1 = self.team1.retrieve_from_team()
        elif action2 == Battle.Action.SWAP:
            self.team2.add_to_team(self.out2)
            self.out2 = self.team2.retrieve_from_team()
        elif action2 == Battle.Action.SPECIAL:
            self.team2.add_to_team(self.out2)
            self.team2.special()
            self.out2 = self.team2.retrieve_from_team()

        if action1 == Battle.Action.ATTACK and action2 == Battle.Action.ATTACK:
            if self.out1.get_speed() > self.out2.get_speed():
                dmg = self.calc_damage(self.out1, self.out2)
                self.out2.set_hp(self.out2.get_hp() - dmg)
                if self.out2.get_hp() <= 0:
                    if len(self.team2) <= 0:
                        return Battle.Result.TEAM1
                    else:
                        self.out2 = self.team2.retrieve_from_team()
            elif self.out1.get_speed() < self.out2.get_speed():
                dmg = self.calc_damage(self.out2, self.out1)
                self.out1.set_hp(self.out1.get_hp() - dmg)
                if self.out1.get_hp() <= 0:
                    if len(self.team1) <= 0:
                        return Battle.Result.TEAM2
                    else:
                        self.out1 = self.team1.retrieve_from_team()
            else:
                dmg = self.calc_damage(self.out1, self.out2)
                self.out2.set_hp(self.out2.get_hp() - dmg)
                dmg = self.calc_damage(self.out2, self.out1)
                self.out1.set_hp(self.out1.get_hp() - dmg)
                if self.out2.get_hp() <= 0 and self.out1.get_hp() <= 0:
                    if len(self.team1) <= 0 and len(self.team2) <= 0:
                        return Battle.Result.DRAW
                    elif len(self.team1) <= 0:
                        return Battle.Result.TEAM2
                    elif len(self.team2) <= 0:
                        return Battle.Result.TEAM1
                    else:
                        self.out1 = self.team1.retrieve_from_team()
                        self.out2 = self.team2.retrieve_from_team()
                elif self.out2.get_hp() <= 0:
                    if len(self.team2) <= 0:
                        return Battle.Result.TEAM1
                    else:
                        self.out2 = self.team2.retrieve_from_team()
                elif self.out1.get_hp() <= 0:
                    if len(self.team1) <= 0:
                        return Battle.Result.TEAM2
                    else:
                        self.out1 = self.team1.retrieve_from_team()

    def calc_damage(self, attacker, defender) -> float:
        if attacker.get_attack() / 2 > defender.get_defense():
            dmg = attacker.get_attack() - defender.get_defense()
        elif self.out1.get_attack() > self.out2.get_defense():
            dmg = (attacker.get_attack() * 5 / 8) - (defender.get_defense() / 4)
        else:
            dmg = attacker.get_attack() / 4
        return dmg

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
        # Add any pregame logic here.
        self.turn_number = 0
        self.team1 = team1
        self.team2 = team2
        self.out1 = team1.retrieve_from_team()
        self.out2 = team2.retrieve_from_team()
        result = None
        while result is None:
            result = self.process_turn()
        # Add any postgame logic here.
        return result


if __name__ == "__main__":
    t1 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    t2 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    b = Battle(verbosity=3)
    print(b.battle(t1, t2))
