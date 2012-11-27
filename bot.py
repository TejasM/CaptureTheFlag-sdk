import util

class Bot():
    STATE_DEFENDING_HORIZONTAL = 0
    STATE_DEFENDING_VERTICAL = 1
    STATE_ATTACKING = 2
    
    enemy_targeting = None
    
    state = None
    
    attacking_partner = None
    
    how_much_danger = 0
      
    def initialize(self, bot):
        self.bot = bot
        
    def getClosestEnemy(self):
        return reduce(lambda x,y: x if util.distanceBetween(x, self.bot.position) <= util.distanceBetween(y, self.bot.position) else y, self.bot.visibleEnemies)