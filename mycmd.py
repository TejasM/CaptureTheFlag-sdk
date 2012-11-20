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


class DefensiveCommander(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """
    numOfDefWanted = 2
    
    targetLeft = (Vector2(0.0, 4.0), Vector2(4.0, 4.0))
    targetAbove = (Vector2(4.0, 0.0), Vector2(4.0, 4.0))
    targetBelow = (Vector2(4.0, 4.0), Vector2(4.0, 0.0))
    defendingTargets = (targetLeft, targetAbove, targetBelow)
    
    
    
    def initialize(self):
        self.attackerPairs = []
        self.defenders = []
        self.enemies = []
        self.curEnemy = None
        if self.game.team.flagScoreLocation.x > 50:
            self.targetBelow, self.targetAbove = self.targetAbove, self.targetBelow
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
            else:
                target = self.game.enemyTeam.flag.position
                flank = self.getFlankingPosition(bot1, target)
                if (target - flank).length() > (bot1.position - target).length():
                    self.issue(commands.Attack, bot1, target, description = 'attack from flank', lookAt=target)
                else:
                    flank = self.level.findNearestFreePosition(flank)
                    self.issue(commands.Attack, bot1, flank, description = 'running to flank')
                flank = self.getFlankingPosition(bot2, target)
                if (target - flank).length() > (bot2.position - target).length():
                    self.issue(commands.Attack, bot2, target, description = 'attack from flank', lookAt=target)
                else:
                    flank = self.level.findNearestFreePosition(flank)
                    self.issue(commands.Attack, bot2, flank, description = 'running to flank')

    def defendBase(self, i, bot):
        targetPosition = self.game.team.flag.position
        targetMin = targetPosition - (self.defendingTargets[i])[0]
        targetMax = targetPosition + (self.defendingTargets[i])[1]      
                
        if bot.flag:
            # bring it hooome
            targetLocation = self.game.team.flagScoreLocation
            self.issue(commands.Charge, bot, targetLocation, description='returning enemy flag!')
        elif targetPosition != self.game.team.flagScoreLocation:
            self.issue(commands.Attack, bot, targetPosition, description='getting my flag!', lookAt=targetPosition)
        else:
            position = self.level.findRandomFreePositionInBox((targetMin, targetMax))
            self.issue(commands.Move, bot, position, description='defending around flag')
    
    def attackAlone(self, bot):
        targetLocation = self.game.team.flagScoreLocation
        if bot.flag:
            self.issue(commands.Charge, bot, targetLocation, description='returning enemy flag!')
        else:
            target = self.game.enemyTeam.flag.position
            flank = self.getFlankingPosition(bot, target)
            if (target - flank).length() > (bot.position - target).length():
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
        if math.acos(cosTheta) <= self.level.FOVangle/2:
            return True
        return False
            
    def tick(self):
        #Update Attackers if one/both died
        for attackerPair in self.attackerPairs[:]:
            if attackerPair[0].health <= 0 or attackerPair[1].health <= 0:
                self.attackerPairs.remove(attackerPair)
                if attackerPair[1].health > 0:
                    self.attackAlone(attackerPair[1])
                elif attackerPair[0].health > 0:
                    self.attackAlone(attackerPair[0])
        #Update Defenders   
        for defender in self.defenders[:]:
            #Remove Defender if dead
            if defender[0].health <=0:
                self.defenders.remove(defender)
                continue
            i = self.defenders.index(defender)
            #If enemy is dead go back to defending base
            if (defender[1] and defender[1].health <= 0) or (defender[1] and not defender[1] in defender[0].visibleEnemies):
                self.enemies.remove(defender[1])
                self.defenders[i] = (defender[0], None)
                self.defendBase(i, defender[0])
            #If enemies are close to shooting distance make them active enemies
            for enemy in defender[0].visibleEnemies:
                if (enemy.position - defender[0].position).length() < self.level.firingDistance + 7.0 and not enemy == defender[1]:
                    self.enemies.append(enemy)
                    self.defenders[i] = (defender[0], enemy)
                    self.issue(commands.Defend, defender[0], enemy.position - defender[0].position, description='defending facing enemy')
                    continue
            #If there is an active enemy and is not in VOF then turn towards him
            if defender[1] and not self.inVOF(defender[0], defender[1]):
                self.issue(commands.Defend, defender[0], defender[1].position - defender[0].position, description='defending facing enemy')
        
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
