from monster_base import MonsterBase
# These classes inherit from MonsterBase,
# but you don't need to implement them explicitly.
from helpers import Infernox, Ironclad, Metalhorn

monster = Metalhorn(True, 1)
print(monster)
monster.level_up()
monster = monster.evolve()
print(monster)