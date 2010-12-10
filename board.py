import numpy as np
import math
from group import Group, MetaGroup
from log import Log
from copy import copy
import random as rand

class Board:

    def __init__(self, boardsize,log):
        """
        Board constructor
        """
        self.__size__ = boardsize         # board size
        self.log = log                    # log file
        
        self.__board__ = np.zeros((self.__size__,self.__size__))  # board
        self.__history__=[]                                       # history of movements
        self.__killedList__=[]                                    # list of killed stones
        
        # setup initial liberties
        self.__initLiberties__()
        
        # matrix containing the initial liberties for each position
        self.__iniLib__ = self.__liberties__.copy()
        self.__groupList__=[]
        self.__metaGroupList__=[]
        
    def __initLiberties__(self):
        """
        Initialize the liberties
        """
        # matrix containing the liberties for each position
        self.__liberties__=np.ones((self.__size__,self.__size__))*4
        self.__liberties__[0,:]=3
        self.__liberties__[self.__size__-1,:]=3
        self.__liberties__[:,self.__size__-1]=3
        self.__liberties__[:,0]=3
        self.__liberties__[0,0]=2
        self.__liberties__[self.__size__-1,0]=2
        self.__liberties__[0,self.__size__-1]=2
        self.__liberties__[self.__size__-1,self.__size__-1]=2
        
    def copy(self):
        """
        Returns a deep copy of the board
        """
        newBoard = Board(self.__size__,self.log)
        newBoard.__groupList__ = copy(self.__groupList__)
        newBoard.__metaGroupList__ = copy(self.__metaGroupList__)
        newBoard.__history__ = copy(self.__history__)
        newBoard.__killedList__ = copy(self.__killedList__)
        newBoard.__liberties__=self.__liberties__.copy()
        return newBoard
        
    def clear(self):
        """
        Clears the board and re-initializes the liberties
        """
        self.__board__ = np.zeros((self.__size__,self.__size__))
        self.__history__=[]
        self.__initLiberties__()
        self.__groupList__=[]
        self.__metaGroupList__=[] 
        
        
    def removeGroup(self,group):
        """
        Removes a group
        """
        self.__groupList__.remove(group)
        
    def removeMetaGroup(self, metaGroup):
        """removeMetaGroup function: 
        
            Removes a 'metaGroup'. 
        
        """
        self.__metaGroupList__.remove(metaGroup)
        
    def update(self,move):
        """
         Updates the board
        """
        movement=move.getListFormat()
        color = movement[0]
        posX = movement[1]
        posY = movement[2]
        
        pos=[posX, posY]
        
        if move.getColor() =='b':
            self.__board__[posX,posY] = 1
        else:
            self.__board__[posX,posY] = 2
            
        # history list update        
        self.__history__.append(movement)        
        
        
        # Store the metagroups attached to the last move: 
        flagMG = False
        bufferMG = []
        for MG in self.__metaGroupList__: 
            if (pos in MG.getBoundry()) and (color == MG.getColor()): 
                bufferMG += [self.__metaGroupList__.pop(self.__metaGroupList__.index(MG))]
        if len(bufferMG)>0: 
            flagMG = True
        #self.log.logDebug("meta-groups buffer: "+str(bufferMG))
        
        # create new "group"
        newGroup=Group(color,[posX,posY])
        
        # creating boundary for the new group 
        newBound=[]
        if pos[0]>0 and self.__board__[pos[0]-1,pos[1]]==0:
            newBound.append([pos[0]-1,pos[1]])
        if pos[0]<self.__size__-1 and self.__board__[pos[0]+1,pos[1]]==0 :
            newBound.append([pos[0]+1,pos[1]]) 
        if pos[1]>0 and self.__board__[pos[0],pos[1]-1]==0:
            newBound.append([pos[0],pos[1]-1])
        if pos[1]<18 and self.__board__[pos[0],pos[1]+1]==0:
            newBound.append([pos[0],pos[1]+1]) 
        
        # assign the boundary to the new group
        newGroup.setBoundAndLib(newBound)

        # checking joined boundaries and creating groups neighbors lists
        groups2join=[newGroup]    # groups to join with the new stone
        newNeighbours=[]          # groups which are neighbors to the new stone 
        
        # loop on all groups
        for group in self.__groupList__:
            
            # the current stone is in the boundary of a group
            if pos in group.getBoundry():  
                newBoundry=group.getBoundry()
                newBoundry.remove(pos)
                group.setBoundAndLib(newBoundry)
                 
                # the new stone is of the same color of the group
                if group.getColor()==color:
                    # there is a group to join
                    groups2join.append(group)
                else:
                    # the new stone is a neighbor of the group
                    newNeighbours.append(group)
                    
                # Check which groups from the MG are those which has 'move' in the boundary: 
                for MG in bufferMG: 
                    if group in MG.getGroups(): 
                        MG.getGroups().pop(MG.getGroups().index(group))
                
        # join the groups
        joinedBoundry=[]              # boundary
        joinedPos=[]                  # positions of the stones in the group
        joinedNeighbs=newNeighbours   # neighbors
        
        # loop over all groups to join
        for group in groups2join:
            joinedBoundry=joinedBoundry+[p for p in group.getBoundry() if p not in joinedBoundry] 
            joinedNeighbs=joinedNeighbs+[g for g in group.getNeighbours() if g not in joinedNeighbs] 
            joinedPos=joinedPos+group.getPos()
            if not group==newGroup:
                self.removeGroup(group)
        
        # set boundary, positions and neighbors of the new group
        newGroup.setBoundAndLib(joinedBoundry)
        newGroup.setPos(joinedPos)
        newGroup.addNeighb(joinedNeighbs)

        # append to the groups' list
        self.__groupList__.append(newGroup)
        
        # delete multiple neighbors from neighboring groups
        for group in joinedNeighbs:
            for g in groups2join:
                if g in group.getNeighbours():
                   group.delNeighb(g) 
            group.addNeighb([newGroup])
        
        # board liberties update
        self.__liberties__[posX,posY]=-10
        if posX>0 and not self.__liberties__[posX-1,posY]==-10:
            self.__liberties__[posX-1,posY]=self.__liberties__[posX-1,posY]-1
        if posX<self.__size__-1 and not self.__liberties__[posX+1,posY]==-10:
            self.__liberties__[posX+1,posY]=self.__liberties__[posX+1,posY]-1
        if posY>0 and not self.__liberties__[posX,posY-1]==-10:
            self.__liberties__[posX,posY-1]=self.__liberties__[posX,posY-1]-1
        if posY<self.__size__-1 and not self.__liberties__[posX,posY+1]==-10:
            self.__liberties__[posX,posY+1]=self.__liberties__[posX,posY+1]-1
            
        
        
        # killing a group and updating board and liberties and neighbors
        killedGroups=[]
        
        # loop over neighbors of the new group
        for group in newGroup.getNeighbours():
            
            # if a group has zero liberty dies
            if group.getLib()==0:             
                killedGroups.append(group)            
                self.removeGroup(group)
        
        # add the killed groups to the list
        self.__killedList__=killedGroups
        
        # loop over killed groups
        for group in killedGroups:
            
            # positions of the killed group
            posList=group.getPos()   
            
            # delete the killed group from the neighbors of its neighbors
            for neighb in group.getNeighbours():
                if group in neighb.getNeighbours():
                    neighb.delNeighb(group)
                
                # restore the board and the liberties after the group has been killed
                for p in posList:    
                     self.__board__[p[0],p[1]]=0
                     self.__liberties__[p[0],p[1]]=self.__iniLib__[p[0],p[1]]
                     
                     # update boundaries
                     if [p[0]+1,p[1]] in neighb.getPos() or [p[0]-1,p[1]] in neighb.getPos() or [p[0],p[1]+1] in neighb.getPos() or [p[0],p[1]-1] in neighb.getPos():
                            neighbBound=neighb.getBoundry()
                            neighbBound.append(p)
                            neighb.setBoundAndLib(neighbBound)    
                            
            # update the liberties
            for p in posList:
                if p[0]<self.__size__-1 and self.__liberties__[p[0]+1,p[1]]==-10:
                    self.__liberties__[p[0],p[1]]=self.__liberties__[p[0],p[1]]-1
                if p[0]>0 and self.__liberties__[p[0]-1,p[1]]==-10:
                    self.__liberties__[p[0],p[1]]=self.__liberties__[p[0],p[1]]-1
                if p[1]<self.__size__-1 and self.__liberties__[p[0],p[1]+1]==-10:
                    self.__liberties__[p[0],p[1]]=self.__liberties__[p[0],p[1]]-1
                if p[1]>0 and self.__liberties__[p[0],p[1]-1]==-10:
                    self.__liberties__[p[0],p[1]]=self.__liberties__[p[0],p[1]]-1                
                    
        # get groups and jointPoints from the stored MG, which will become the groups and jP of the new MG. 
        if flagMG: 
            bufferGroups = [newGroup] 
            bufferJP = []
            for MG in bufferMG: 
                bufferGroups += MG.getGroups()
                bufferJP += MG.getJointPoints()
            newMG = MetaGroup(color, bufferGroups, bufferJP)
            self.__metaGroupList__ += [newMG]
            self.log.logDebug(str(newMG.getGroups()))
            self.log.logDebug(str(newMG.getBoundry()))
              
        # check last move for eye (both simple and complex)      
        self.checkLastMoveForEye(move)
        
        # in case we had meta-groups they need to be updted
        if flagMG: 
            newMG.update()
        
        # debug    
        nEyes = 0
        for group in self.__groupList__: 
            nEyes += len(group.getEye())
            
        #self.log.logDebug("Nr. of eyes: "+str(nEyes))
        #self.log.logDebug("Nr. of meta-groups: "+str(len(self.__metaGroupList__)))
    

    def checkLastMoveForEye(self,move):
        """checLastMoveForEye function: 
        
            This function checks --through 'checkEye()' if any of the positions surrounding a move are an eye--. 
        
        """
        
        # Get move in list format ['color', x, y]
        moveList = move.getListFormat()
        
        # Loops around this position and tells the routine 'chechEye()' to check if any of the surrounding positions became an Eye. 
        sillyIndex = sillyIndex = [[1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1], [0,-1], [1,-1]]
        for index in sillyIndex:
            sillyMove = [moveList[0], moveList[1]+index[0],moveList[2]+index[1]]
            if (sillyMove[1]>-1 and sillyMove[1]<self.__size__) and (sillyMove[2]>-1 and sillyMove[2]<self.__size__): 
                self.checkEye(sillyMove)
        
        
    def checkEye(self, move): 
        """checkEye function: 
        
            This function checks if an eye was created by 'move'. If so, it attached the Eye to the corresponding group. 
            
        """
        
        # Translates list format into matrix format [x,y]: we don't care about the color of maybeEye
        maybeEye = [move[1],move[2]]
        # Get attached groups of the potential Eye. 
        attachedGroups = [group for group in self.__groupList__ if maybeEye in group.getBoundry()] 
        
        #Define some useful indexes. 
        sillyIndex = sillyIndex = [[1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1], [0,-1], [1,-1]]
        halfSillyIndex = [[1,0], [0,1], [-1,0], [0,-1]]
        diagSillyIndex = [[1,1], [-1,1], [-1,-1], [1,-1]]
    
        if (self.__liberties__[maybeEye[0]][maybeEye[1]] != 0) or (self.__liberties__[maybeEye[0]][maybeEye[1]] == -10):
            return 
    
        # Sets counts to zero: 
        wCount = 0
        bCount = 0
        countBound = 0
        # Loop to check if the maybeEye is surrounded by four stones of the same color. 
        for index in halfSillyIndex: 
            adPos = [maybeEye[0]+index[0],maybeEye[1]+index[1]]
            if (adPos[0]>-1 and adPos[0]<self.__size__) and (adPos[1]>-1 and adPos[1]<self.__size__): 
                if self.__board__[adPos[0]][adPos[1]] == 1:  
                    bCount += 1
                elif self.__board__[adPos[0]][adPos[1]] == 2: 
                    wCount += 1
            else: 
                countBound += 1

        # Assigning color to the eye, in case it's wrapped by stones of the same color        
        if bCount != 0 and wCount != 0:
            return
        if bCount + countBound == 4:
            eyeColor = 'b'
        else:
            eyeColor = 'w'
        
        # Set counts to zero: 
        countEyeColor = 0
        countOppColor = 0
        countBound = 0
        # Check the color of the stones in the diagonal positions: 
        for index in diagSillyIndex:
            diagPos = [maybeEye[0]+index[0],maybeEye[1]+index[1]]
            if (diagPos[0]>-1 and diagPos[0]<self.__size__) and (diagPos[1]>-1 and diagPos[1]<self.__size__): 
                for group in self.__groupList__: 
                    if (diagPos in group.getPos()) or (diagPos in group.getEye()): 
                        if group.getColor() == eyeColor: 
                            countEyeColor += 1 
                        else: 
                            countOppColor += 1
            else: 
                countBound += 1
                    
        flagComplex = True
        if (countEyeColor>2 and countBound==0) or (countEyeColor==2 and countBound==2) or (countEyeColor==1 and countBound==3):
            flagComplex = False
            for group in self.__groupList__: 
                if maybeEye in group.getBoundry():
                    group.addEye(maybeEye)
                    self.log.logDebug(str(maybeEye))
                    
        # If the code came up to here but it was not found yet that the prospective Eye is an actual Eye, then the eye constitutes the jointPoint of a MetaGroup and it must be checked from global properties of the MetaGroup if this jointPoint is an actual Eye: 
        if flagComplex: 
            self.checkComplexEyes(maybeEye, eyeColor)
        
    def checkComplexEyes(self, maybeEye, eyeColor): 
        """checkComplexExes function: 
        
        	This function gets a 'maybeEye' and creates the metagroup formed by the groups and metagroups attached to it. By doing this, the complex eyes in the new metagroup are calculated. 
        
        """
        
        attMGroups = [] 
        jointPoints = [maybeEye]
        attachedGroups = []
        for MG in self.__metaGroupList__: 
            if maybeEye in MG.getBoundry(): 
                attMGroups += [self.__metaGroupList__.pop(self.__metaGroupList__.index(MG))]
        for MG in attMGroups: 
            attachedGroups += [group for group in MG.getGroups()]
            jointPoints += [jP for jP in MG.getJointPoints()]
        for group in self.__groupList__:
            if (group not in attachedGroups) and (maybeEye in group.getBoundry()):
                attachedGroups += [group]
        #self.log.logDebug("attached groups"+str(attachedGroups))
        self.__metaGroupList__ += [MetaGroup(eyeColor, attachedGroups, jointPoints)]
                
    def showBoard(self):
        """
        Returns a string representation of the board
        """
        boardStr = '\n     A   B   C   D   E   F   G   H   J   K   L   M   N   O   P   Q   R   S   T\n'
        for row in xrange(self.getSize()):
            numStr = ' '+str(self.__size__-row) if row > 9 else str(self.__size__-row)
            boardStr = boardStr + numStr+'   '
            for col in xrange(self.getSize()):
                el = self.__board__[row][col]
                if el == 0:
                    elStr = '.'
                elif el == 1:
                    elStr = 'b'
                elif el == 2:
                    elStr = 'w'
                boardStr = boardStr + elStr + '   '
            boardStr = boardStr+ numStr+'\n'
        boardStr =  boardStr+'\n     A   B   C   D   E   F   G   H   J   K   L   M   N   O   P   Q   R   S   T\n'

        return boardStr


    def evaluate(self):
        """
        Evaluates the state of the game: returns the winner as Black or White
        """
        nEyesB=0
        nStonesB=0
        nEyesW=0
        nStonesW=0
        nB=0
        nW=0
        
        for g in self.getGroups():
            if g.getColor()=='b' :
                eye=g.getEye()
                nEyesB+=len(eye)
                nStonesB+=len(g.getPos())
            
            if g.getColor()=='w' :
                eye=g.getEye()
                nEyesW+=len(eye)
                nStonesW+=len(g.getPos())
                
        nB=nEyesB+nStonesB
        nW=nEyesW+nStonesW
        
        #print 'black scores: ',nB
        #print 'white scores: ',nW
        
        if nB>nW:
            return 'Black'
        elif nB<nW:
            return 'White'
        else:
            return rand.choice(['Black','White'])
           
   
    def renormCluster(self,cluster): 
        """renormCluster function: 
  
          This function gets a list with the colors of the positions played in four positions which are the corners 
          of a common square and gives back the color of the renormalized cluster. 
      
        Gets: 
            ==> cluster: list with the colors. 
        Returns: 
            ==> color: color of the renormalized cluster. 
            ==> numEmpty: number of empty positions of the unfolded cluster. 
  
        """
  
        bCount = sum(sum(cluster == 1))
        wCount = sum(sum(cluster == 2))
        numEmpty=cluster.size-bCount-wCount

        if bCount == 0 and wCount == 0:
            color = 0
        elif bCount > wCount:
            color = 1
        elif bCount < wCount:
            color = 2
        else: 
            if rand.random() > 0.5:
                color = 1
            else:
                color = 2
      
        return [color, numEmpty, bCount, wCount]
  
  
    def renormalize(self,wSize = 2):
        extraRC = np.mod(self.__size__,wSize)
        codeExtraRC = 4
  
        tmpBoard = np.ones((self.__size__+extraRC,self.__size__+extraRC))*codeExtraRC
        tmpBoard[0:self.__size__,0:self.__size__] = self.__board__
        
        renBoardSize = tmpBoard.shape[0] / wSize
        renBoardData = [[[] for i in xrange(renBoardSize)] for j in xrange(renBoardSize)]
 
        for x in xrange(renBoardSize):
            for y in xrange(renBoardSize):
                cluster = tmpBoard[wSize*x:wSize*(x+1),wSize*y:wSize*(y+1)]
                renBoardData[x][y]=self.renormCluster(cluster)   # [color,numEmpty,bCount,wCount]

        return renBoardData
    
    
    def getLastMove(self):
        if not len(self.__history__)==0:
            return self.__history__[-1]
        else: return None

    def getPos(self):
        return self.__board__
    
    def getGroups(self):
        return self.__groupList__


    def getSize(self):
        return self.__size__
    
    def getKilled(self):
        return self.__killedList__

    def getBoardLib(self):
        return self.__liberties__
