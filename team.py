from __future__ import annotations

import math
from enum import auto
from typing import Optional, TYPE_CHECKING

import helpers
from base_enum import BaseEnum
from data_structures.sorted_list_adt import ListItem
from data_structures.array_sorted_list import ArraySortedList
from data_structures.queue_adt import CircularQueue
from data_structures.referential_array import ArrayR
from data_structures.stack_adt import ArrayStack
from helpers import get_all_monsters
from monster_base import MonsterBase
from random_gen import RandomGen

if TYPE_CHECKING:
    from battle import Battle


class MonsterTeam:
    class TeamMode(BaseEnum):

        FRONT = auto()
        BACK = auto()
        OPTIMISE = auto()

    class SelectionMode(BaseEnum):

        RANDOM = auto()
        MANUAL = auto()
        PROVIDED = auto()

    class SortMode(BaseEnum):

        HP = auto()
        ATTACK = auto()
        DEFENSE = auto()
        SPEED = auto()
        LEVEL = auto()

    TEAM_LIMIT = 6

    def __init__(self, team_mode: TeamMode, selection_mode, **kwargs) -> None:
        # Add any pre-init logic here.
        self.team_mode = team_mode
        try:
            self.sort_mode = kwargs["sort_key"]
        except:
            self.sort_mode = MonsterTeam.SortMode.HP
        try:
            self.provided_monsters = kwargs["provided_monsters"]
        except:
            pass

        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            self.team = ArrayStack(self.TEAM_LIMIT)
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            self.team = CircularQueue(self.TEAM_LIMIT)
        elif self.team_mode == MonsterTeam.TeamMode.OPTIMISE:
            self.team = ArraySortedList(self.TEAM_LIMIT)
        else:
            raise ValueError(f"team_mode {team_mode} not supported")

        if selection_mode == self.SelectionMode.RANDOM:
            self.select_randomly()
        elif selection_mode == self.SelectionMode.MANUAL:
            self.select_manually()
        elif selection_mode == self.SelectionMode.PROVIDED:
            self.select_provided()
        else:
            raise ValueError(f"selection_mode {selection_mode} not supported.")

    def __len__(self):
        return len(self.team)

    def add_to_team(self, monster: MonsterBase):
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            self.team.push(monster)
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            self.team.append(monster)
        else:
            if not isinstance(monster, ListItem):
                if self.sort_mode == MonsterTeam.SortMode.HP:
                    monster = ListItem(monster, monster.get_hp())
                elif self.sort_mode == MonsterTeam.SortMode.ATTACK:
                    monster = ListItem(monster, monster.get_attack())
                elif self.sort_mode == MonsterTeam.SortMode.DEFENSE:
                    monster = ListItem(monster, monster.get_defense())
                elif self.sort_mode == MonsterTeam.SortMode.HP.SPEED:
                    monster = ListItem(monster, monster.get_speed())
                else:
                    monster = ListItem(monster, monster.get_level())
            self.team.add(monster)

    def retrieve_from_team(self) -> MonsterBase:
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            return self.team.pop()
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            return self.team.serve()
        else:
            ret = self.team[0]
            self.team.delete_at_index(0)
            return ret

    def special(self) -> None:
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            temp_stack = ArrayStack(self.TEAM_LIMIT)
            new_stack = ArrayStack(self.TEAM_LIMIT)
            while len(self.team) > 3:
                temp_stack.push(self.team.pop())
            while not self.team.is_empty():
                new_stack.push(self.team.pop())
            while not temp_stack.is_empty():
                new_stack.push(temp_stack.pop())
            self.team = new_stack
        elif self.team_mode == MonsterTeam.TeamMode.BACK:
            mid_point = math.ceil((len(self.team) / 2))
            print(mid_point, len(self.team))
            temp_stack = ArrayStack(self.TEAM_LIMIT)
            temp_queue = CircularQueue(self.TEAM_LIMIT)
            while len(self.team) > mid_point:
                temp_queue.append(self.team.serve())
            while not self.team.is_empty():
                temp_stack.push(self.team.serve())
            while not temp_stack.is_empty():
                self.team.append(temp_stack.pop())
            while not temp_queue.is_empty():
                self.team.append(temp_queue.serve())
        else:
            reordered = ArrayStack(self.TEAM_LIMIT)
            for i in range(len(self.team)):
                mon = self.retrieve_from_team()
                mon.key = mon.key * -1
                reordered.append(mon)
            while reordered.length > 0:
                self.add_to_team(reordered.pop())

    def regenerate_team(self) -> None:
        raise NotImplementedError

    def select_randomly(self, **kwargs):
        team_size = RandomGen.randint(1, self.TEAM_LIMIT)
        monsters = get_all_monsters()
        n_spawnable = 0
        for x in range(len(monsters)):
            if monsters[x].can_be_spawned():
                n_spawnable += 1

        for _ in range(team_size):
            spawner_index = RandomGen.randint(0, n_spawnable - 1)
            cur_index = -1
            for x in range(len(monsters)):
                if monsters[x].can_be_spawned():
                    cur_index += 1
                    if cur_index == spawner_index:
                        # Spawn this monster
                        self.add_to_team(monsters[x]())
                        break
            else:
                raise ValueError("Spawning logic failed.")

    def select_manually(self):
        """
        Prompt the user for input on selecting the team.
        Any invalid input should have the code prompt the user again.

        First input: Team size. Single integer
        For _ in range(team size):
            Next input: Prompt selection of a Monster class.
                * Should take a single input, asking for an integer.
                    This integer corresponds to an index (1-indexed) of the helpers method
                    get_all_monsters()
                * If invalid of monster is not spawnable, should ask again.

        Add these monsters to the team in the same order input was provided. Example interaction:

        How many monsters are there? 2
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 38
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 2
        This monster cannot be spawned.
        Which monster are you spawning? 1
        """

        team_size = None

        while not isinstance(team_size, int):
            try:
                team_size = int(input("How many monsters are there? "))
            except ValueError:
                print("Enter a valid integer")
            if team_size > MonsterTeam.TEAM_LIMIT:
                print(f"Team size must be between 1 and {MonsterTeam.TEAM_LIMIT}")
                team_size = None

        monster_list = helpers.get_all_monsters()
        print("Monsters are: ")
        for i in range(len(monster_list)):
            spawnable = "❌"
            if monster_list[i].can_be_spawned():
                spawnable = "✔️"
            to_print = i + 1, str(monster_list[i])[12:-2], spawnable
            print(to_print)
        for i in range(team_size):
            new_mon = None
            while not isinstance(new_mon, int):
                try:
                    new_mon = int(input("Which monster are you spawning? ")) - 1
                except ValueError:
                    print("Please input an integer")
                if not monster_list[new_mon].can_be_spawned():
                    print("Selected monster can't be spawned, please select another")
                    new_mon = None
            self.add_to_team(monster_list[new_mon]())

    def select_provided(self, provided_monsters: Optional[ArrayR[type[MonsterBase]]] = None):
        """
        Generates a team based on a list of already provided monster classes.

        While the type hint imples the argument can be none, this method should never be called without the list.
        Monsters should be added to the team in the same order as the provided array.

        Example input:
        [Flamikin, Aquariuma, Gustwing] <- These are all classes.

        Example team if in TeamMode.FRONT:
        [Gustwing Instance, Aquariuma Instance, Flamikin Instance]
        """
        if provided_monsters is None:
            raise ValueError
        if self.team_mode == MonsterTeam.TeamMode.FRONT:
            for i in reversed(range(len(provided_monsters))):
                self.add_to_team(provided_monsters[i])
        else:
            for i in range(len(provided_monsters)):
                self.add_to_team(provided_monsters[i])

    def choose_action(self, currently_out: MonsterBase, enemy: MonsterBase) -> Battle.Action:
        # This is just a placeholder function that doesn't matter much for testing.
        from battle import Battle
        if currently_out.get_speed() >= enemy.get_speed() or currently_out.get_hp() >= enemy.get_hp():
            return Battle.Action.ATTACK
        return Battle.Action.SWAP


if __name__ == "__main__":
    team = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.OPTIMISE,
        selection_mode=MonsterTeam.SelectionMode.MANUAL,
        sort_key=MonsterTeam.SortMode.HP,
    )
    print(team)
    team.special()
    print(team)
