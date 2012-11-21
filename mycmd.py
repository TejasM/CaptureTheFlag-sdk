# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.
from api import Commander

# The commander can send 'Commands' to individual bots.  These are listed and
# documented in commands.py from the ./api/ folder also.
from api import commands

# The maps for CTF are layed out along the X and Z axis in space, but can be
# effectively be considered 2D.
from api import Vector2
import math
import sys


def distance(vector1, vector2):
    return (vector1-vector2).length();

def distanceBetween(bot1, bot2):
    return distance(bot1.position, bot2.position)

class DefensiveCommander(Commander):
    """
    Intelligence Objects
    """
    #enemies in radius:
    radius = 35.0
    closeEnemies = set()
    
    flagGone = False
    
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """
    numOfDefWanted = 3
    
    targetLeft = Vector2(-1.0, 0.0)
    targetAbove = Vector2(0.0, -1.0)
    targetBelow = Vector2(0.0, 1.0)
    defendingTargets = ()
    
    def gatherIntel(self):
        self.closeEnemies = set()
        bots = self.game.bots_alive
        flagPosition = self.game.team.flag
        for bot in bots:
            for enemy in bot.visibleEnemies:
                if distanceBetween(enemy, flagPosition) < self.radius and enemy.health > 0:
                    self.closeEnemies.add(enemy)
        if self.game.team.flag.position != self.game.team.flagScoreLocation:
            self.flagGone = True
        else:
            self.flagGone = False
    
    
    def initialize(self):
        self.attackerPairs = []
        self.defenders = []
        self.enemies = set() 
        self.curEnemy = None
        if self.game.team.flagScoreLocation.x > self.level.width/2:
            self.targetLeft = Vector2(1.0, 0.0)
        self.defendingTargets = (self.targetLeft, self.targetAbove, self.targetBelow)

            
            
        #Flanking Stuff
        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) / 2.0
    
        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()
        
    def getFlankingPosition(self, bot, target):
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (bot.position - p).length())[0]

    def attackInPair(self, bots, i):
        bot1 = bots[i]
        bot2 = bots[i+1]
        pairOfAttackers = (bot1, bot2)
        if pairOfAttackers in self.attackerPairs:
            return
        else:
            self.attackerPairs.append(pairOfAttackers)
            if bot1.flag or bot2.flag:
                # bring it hooome
                targetLocation = self.game.team.flagScoreLocation
                self.issue(commands.Charge, bot1, targetLocation, description='returning enemy flag!')
                self.issue(commands.Charge, bot2, targetLocation, description='returning enemy flag!')
            elif self.flagGone:
                targetLocation = self.game.team.flag.position
                self.issue(commands.Attack, bot1, targetLocation, description='Getting our flag!')
                self.issue(commands.Attack, bot2, targetLocation, description='Getting our flag!')
            else:
                target = self.game.enemyTeam.flag.position
                flank = self.getFlankingPosition(bot1, target)
                if  target and (target - flank).length() > (bot1.position - target).length():
                    self.issue(commands.Attack, bot1, target, description = 'attack from flank', lookAt=target)
                else:
                    flank = self.level.findNearestFreePosition(flank)
                    self.issue(commands.Attack, bot1, flank, description = 'running to flank')
                flank = self.getFlankingPosition(bot2, target)
                if target and (target - flank).length() > (bot2.position - target).length():
                    self.issue(commands.Attack, bot2, target, description = 'attack from flank', lookAt=target)
                else:
                    flank = self.level.findNearestFreePosition(flank)
                    self.issue(commands.Attack, bot2, flank, description = 'running to flank')
    
    def inArea(self, position, target):
        if distance(position, target) < 0.75:
            return True
        return False
    
    def defendBase(self, i, bot):
        targetPosition = self.game.team.flag.position
        targetMin = targetPosition - self.defendingTargets[i]    
                
        if bot.flag:
            # bring it hooome
            targetLocation = self.game.team.flagScoreLocation
            self.issue(commands.Charge, bot, targetLocation, description='returning enemy flag!')
        elif self.flagGone:
            self.issue(commands.Attack, bot, targetPosition, description='getting my flag!')
        elif not self.inArea(bot.position, targetMin):
            position = self.level.findNearestFreePosition(targetMin)
            self.issue(commands.Move, bot, position, description='defending around flag')
        elif bot.state != 2:
            self.issue(commands.Defend, bot, -(self.defendingTargets[i]), description="Defending base")
    
    def attackAlone(self, bot):
        targetLocation = self.game.team.flagScoreLocation
        if bot.flag:
            self.issue(commands.Charge, bot, targetLocation, description='returning enemy flag!')
        else:
            target = self.game.enemyTeam.flag.position
            flank = self.getFlankingPosition(bot, target)
            if target and (target - flank).length() > (bot.position - target).length():
                self.issue(commands.Attack, bot, target, description = 'attack from flank', lookAt=target)
            else:
                flank = self.level.findNearestFreePosition(flank)
                self.issue(commands.Move, bot, flank, description = 'running to flank')
            
    def isBotDefender(self, bot):
        for defender in self.defenders:   
            if defender[0] == bot:
                return True
        return False
    
    def hasEnemies(self, bot):
        for defender in self.defenders:   
            if defender[0] == bot:
                if defender[1]:
                    return True
        return False
    
    def inVOF(self, bot, enemy):
        facing = bot.facingDirection
        neededDir = enemy.position - bot.position
        cosTheta = (facing.x*neededDir.x + facing.y*neededDir.y)/(facing.length()*neededDir.length())
        if cosTheta >1:      
            cosTheta = 1
        if math.acos(cosTheta) <= self.level.FOVangle/2.5:
            return True
        return False
    
    def getClosestEnemy(self, bot):
        if len(bot.visibleEnemies) == 0:
            return None
        if len(bot.visibleEnemies) == 1:
            if bot.visibleEnemies[0].health > 0:
                return bot.visibleEnemies[0]
            else:
                return None
        enemy = reduce(lambda x,y: x if x.health > 0 and (x.position-bot.position).length() <= (y.position - bot.position).length() else y, bot.visibleEnemies)
        if enemy.health > 0:
            return enemy
        else:
            return None
    
    def findClosestDefender(self, enemy, defenders):
        if len(defenders)==0:
            return None;
        if len(defenders)==1:
            return defenders[0]
        return reduce(lambda x,y: x if distanceBetween(enemy, x[0]) <= distanceBetween(enemy, y[0]) else y, defenders)
    def enemiesCloseBy(self, enemy, enemies):
        closeEnemies = [enemy]
        for enemy2 in enemies:
            if enemy2 != enemy:
                if distanceBetween(enemy2, enemy) < 3.0:
                    closeEnemies.add(enemy2)
        return closeEnemies
        
    def orderDefenders(self):
        for defender in self.defenders[:]:
        #Remove Defender if dead
            if defender[0].health <= 0:
                self.defenders.remove(defender)
            elif defender[1] and (defender[1].health <=0 or not defender[1] in self.closeEnemies or not defender[1] not in defender[0].visibleEnemies):
                self.defenders[self.defenders.index(defender)] = (defender[0], None)       
                
        defendersAvailable = filter(lambda x: x[1]==None, self.defenders)
        for enemy in self.closeEnemies:
            defender = self.findClosestDefender(enemy, defendersAvailable)
            if defender and defender[0]:
                defendersAvailable.remove(defender)
                self.defenders[self.defenders.index(defender)] = (defender[0], enemy)
                self.issue(commands.Defend, defender[0], enemy.position - defender[0].position, description="Defending against closest enemy")

        for i, defendersDoingNothing in enumerate(defendersAvailable):
            self.defendBase(i, defendersDoingNothing[0])
        
    def tick(self):
        
        self.gatherIntel()
        
        #Update Attackers if one/both died
        for attackerPair in self.attackerPairs[:]:
            if attackerPair[0].health <= 0 or attackerPair[1].health <= 0:
                self.attackerPairs.remove(attackerPair)
                if attackerPair[1].health > 0:
                    self.attackAlone(attackerPair[1])
                elif attackerPair[0].health > 0:
                    self.attackAlone(attackerPair[0])
                    
        #Update Defenders   
        self.orderDefenders()
        
        
        #If there are still bots idle:
        bots = self.game.bots_available
        
        for i, bot in enumerate(bots):
            if len(self.defenders)>=self.numOfDefWanted and not self.isBotDefender(bot):
                if  i%2==1 and len(bots) != i+1:
                    self.attackInPair(bots, i)
                elif not self.isBotDefender(bot):
                    self.attackAlone(bot)                    
            else:
                # defend the flag!
                if not self.isBotDefender(bot):
                    self.defenders.append((bot, None))
                if self.hasEnemies(bot):
                    continue
                else:                    
                    self.defendBase(self.defenders.index((bot, None)), bot)
           
                            

    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass
