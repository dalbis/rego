
"""

This file is part of ReGo, a Go program. 

Contact: 
	>> Tiziano D'Albis: tiziano.dalbis@gmail.com 
	>> Lovisa Irpa Helgadottir: loairpa@gmail.com 
	>> Saikat Ray: deltaray224@gmail.com
	>> Hadi Roohani: hadirhn@gmail.com
	>> Helene Schmidt: heleneschmi@googlemail.com 
	>> Luis F. Seoane: brigan@gmail.com 

Copyright 2010 and 2011 by Tiziano D'Albis, Lovisa Irpa Helgadottir, Saikat Ray, Hadi Roohani, Helene Schmidt and Luis F. Seoane. 

ReGo is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by

the Free Software Foundation either version 3 of the License, or (at your option) any later version. 

ReGo is distributed with the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 

MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License in file COPYING for more details. 

You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>. 

"""


"""

Player class and stuff. 

"""

import numpy as np
import random as rand
import move as M


class Player(): 
    """Player class: 
    
    Attributes: 
        ==> __board__: board in which 'player' plays. 
        ==> __color__: especifies the color of the player. 
            >> 'B', 'W'
        ==> __log__: log to debug. 
        ==> __listLegal__: list with legal movements for this player. 
        
    Functions: 
        ==> __init__(): initializes the object. 
        ==> getBoard(), getColor(), getListLegal(): returns the attribute. 
        ==> genMove(): generates a legal move. 
        ==> updateListLegal(): updates listLegal after movement or with the movements of the other player. 
        ==> appendListLegal(): appends movements which became legal to listlegal. It avoids repetitions. 
        ==> numToMove(): converts a number into a move. 
        ==> moveToNum(): converts a move into a number. 
        ==> renormCluster(): renormalizes a cluster. 
        ==> getClusterList(): sorts the board into clusters ready to be renormalized. 
    
    """
    
  
    
    def __init__(self, color, board, log, listLegal = None):
        """__init__ function for Player: 
        
            This function initializes objects of the Player class. 
            
        Attributes: 
            ==> color: sets the color of self. 
            ==> board: sets the board of self. 
            [==> listLegal]: in case a board with an advanced game is given, a list of legal movements might be provided. 
        
        """
        
        self.__board__ = board
        self.__color__ = color
        
        self.__log__ = log

        if listLegal is None:
            self.__listLegal__ = [ii for ii in range(self.__board__.getSize()**2)]
        else: 
            self.__listLegal__ = listLegal
            
        self.__KO__ = None
        
    ##############################################################################
    ## Gets: 
        
    def getBoard(self): 
        return self.__board__
        
    def getColor(self):
        return self.__color__
        
    def getListLegal(self): 
        return self.__listLegal__
           
    ## Gets. 
    ##############################################################################
        
            
    def genMove(self): 
        """genMove function: 
        
            This function returns a legal move for player self. 
            
            To be implemented: legal intelligent moves. 
        
        """
        
        if (len(self.__listLegal__) == 0): 
            return None
        else: 
            index = rand.randint(0,len(self.__listLegal__)-1)
            num = [self.__color__,self.__listLegal__[index]]
            move = self.numToMove(num)
            if self.__KO__ is not None:
                numKO = self.moveToNum(self.__KO__)
                self.appendListLegal(numKO[1])
                self.__KO__ = None
            
        # Go board don't have "I"!! 
        lettList=['A','B','C','D','E','F','G','H','J','K','L','M','N','O','P','Q','R','S','T']
        return M.Move(posLetter=lettList[move[2]], posNumber=19-move[1],color=move[0])
        
    
    ##############################################################################
    ## Methods Keep the list of legal moves updated: 
    
    def updateListLegal(self, move=None, listKilledGroup=None):
        """update_listLegal function: 
        
            This function updates 'listLegal' removing 'move' and checking whether the positions attached to 'move' are legal or not. Also some movements which were ilegal before, become legal now. 
            
        Check for KO: 
            KO is marcked in 'self.board.getPos()' with a three after a move has been made, so we straightforwardly read KOs from the board. 
            
        Check for Eyes: 
            We do already know that a position is surrounded because it has zero liberties (if it has more than 0 we do not have to check this position). Since it has 0 liberties, we can only play there if when playing we kill any of the surrounding groups. Thus forbid the move UNLESS any of the surrounding groups has 1 liberty. 
            It is not necessary to take into account the edges of the board --automatically done. 
            
        Check for Suicide: 
            Again, a position has 0 liberties so we know it is surrounded, but in this case we might find some groups with 'self.color'. In this case, we are allowed to play if we do not commit suicide. Thus we forbid the move UNLESS any of the surrounding groups of the same color has more than 1 liberty. 
        
        """
        
        # Loading obejects which might be usefull for the routine, so there's no need to call them the whole time. 
        sillyIndex = [[1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1], [0,-1], [1,-1]]
        halfSillyIndex = [[1,0], [0,1], [-1,0], [0,-1]]
        actualBoard = self.__board__.getPos()
        actualEmBoardLib = self.__board__.getBoardLib()
        actualGroupList = self.__board__.getGroups()
        releaseList = [] # This variable stores the positions which became legal at the end of the function. 
                         # It's added because in older versions some moves were first released and the forbidden again. 
        
        # Debug: 
#        self.__log__.logDebug(str(actualGroupList))
#        self.__log__.logDebug(self.__board__.showBoard())
 
        

# Updating listLegal with the killed groups: 
# Checked!! 
        if (listKilledGroup is not None) and (len(listKilledGroup) > 0): 
            for killedGroup in listKilledGroup: 
                # Load the neighbours of the killed group: 
                attachedGroups = killedGroup.getNeighbours() 
                # All the positions of the captured stones are released: 
                # Checked! 
                for pos in killedGroup.getPos(): 
                    num = self.moveToNum([killedGroup.getColor(),pos[0],pos[1]])
                    self.appendListLegal(num[1])
                    
                # If the killed group has a different color than 'self', it's possible that the capture 
                # allows to play in a position which was suicide before. 
                # Checked! 
                if killedGroup.getColor() != self.__color__:
                    for group in attachedGroups:
                        # The boundry of the blocks attached to the killed stones. The eyes remain not legal. 
                        releaseList = [pos for pos in group.getBoundry() if pos not in group.getEye()] 
                        for pos in releaseList: 
                            num = self.moveToNum([group.getColor(),pos[0],pos[1]])
                            self.appendListLegal(num[1])
                #     If any of the neighbours groups of the killed group has an eye which was in list legal -meaning it was 
                # allowed to play in the eye and thus kill the group-, now the eyes are not allowed to be played anymore 
                # because the threatened group became more liberties: 
                # Checked! 
                for group in attachedGroups: 
                    for eye in group.getEye(): 
                        num = self.moveToNum([group.getColor(),pos[0],pos[1]])
                        self.popListLegal(num)
        
        if move is not None: 
            # Getting the groups attached to the last played position. 
            actualAttachedGroups = [group for group in actualGroupList if [move[1],move[2]] in group.getBoundry()]
            # Getting the group to which the played position belongs. 
            for group in actualGroupList:
                if [move[1],move[2]] in group.getPos(): 
                    actualGroup = group
        
# Removing the last played position: 
# Checked! 
            #   Remove from 'listLegal' the position which has been played right now. 
            num = self.moveToNum(move)
            self.popListLegal(num[1])
            
#Removing eyes with color of self: 
# Checked! But not tested. 
            #     If 'move' is of the same color as 'self', we check if we formed an eye and we ban this position to be played 
            # by ourselves. 
            if move[0] == self.__color__:
                for sillyMove in sillyIndex: 
                    if (sillyMove in actualGroup.getEye()): 
                        sillyNum = self.moveToNum([move[0],sillyMove[0],sillyMove[1]])     #This piece of code 
                        self.popListLegal(sillyNum[1])           #removes from listLegal. 
                    
# Removing eyes of different color: 
# Checked! But not tested. 
            #     If 'move' is not of the same color as 'self' and it creates an eye, 'self' can not play in this eye unless 
            # playing there would kill an enemy group. 
            if move[0] != self.__color__: 
                for sillyMove in sillyIndex: 
                    if (sillyMove in actualGroup.getEye()) and (actualGroup.getLib() > 1): 
                        sillyNum = self.moveToNum([move[0],sillyMove[0],sillyMove[1]])     #This piece of code 
                        self.popListLegal(sillyNum[1])           #removes from listLegal. 
                            
# Removing suicide of the same color: 
# Checked! But not tested. 
            #     If the group to which the played stone belongs is left with only one liberty, this has to be 
            # removed from 'listLegal' since playing there would cause suicide. 
            # Even though, we also have to check that playing in this only liberty we don't kill an opponent. 
            # If so, this liberty remains legal. 
            if (actualGroup.getColor() == self.__color__) and actualGroup.getLib() == 1: 
                flagRemove = True 
                forbidMove = [actualGroup.getColor(), actualGroup.getBoundry()[0][0], actualGroup.getBoundry()[0][1]]
                for group in actualGroupList:
                    if (group.getColor() != self.__color__) and ([forbidMove[1],forbidMove[2]] in group.getBoundry()) and (group.getLib() == 1): # If there isn't any opponent block with one liberty: 
                        flagRemove = False
                    if (group.getColor() == self.__color__) and ([forbidMove[1],forbidMove[2]] in group.getBoundry()) and (group.getLib() > 2): 
                        flagRemove = False
                
                if flagRemove: 
                    forbidNum = self.moveToNum(forbidMove)
                    self.popListLegal(forbidNum[1])
            
# Removing suicide of different color! 
# Checked! But not tested. 
            #     A move with color different than 'self' was made, that leaves one group of 'self' with only one liberty. 
            # In this case, playing this liberty would be suicide UNLESS playing there would kill any of the groups 
            # attached to the threatened one. 
            if (actualGroup.getColor() != self.__color__): 
                for group in actualAttachedGroups: 
                    if (group.getColor() == self.__color__) and (group.getLib() == 1): 
                        flagRemove = True
                        forbidMove = [group.getColor(), group.getBoundry()[0][0], group.getBoundry()[0][1]]
                        groupsAtt = [attGroup for attGroup in actualGroup if attGroup in group.getNeighbours()] 
                        for attGroup in groupsAtt: 
                            if attGroup.getLib() == 1: 
                                flagRemove = False
                        if flagRemove:
                            forbidNum = self.moveToNum(forbidMove)
                            self.popListLegal(forbidNum[1])
                    
# Appending eye of different color left with only 1 lib: 
# Checked! But not tested. 
            #     If a move has left a group of the opposite color as 'self' with only one liberty left, this liberty becomes 
            # playable in case it was not. 
            for group in actualAttachedGroups:
                if (group.getColor() != self.__color__) and (group.getLib() == 1): 
                    forbidNum = self.moveToNum(group.getColor(),group.getBoundry()[0][0],group.getBoundry()[0][1])
                    self.appendListLegal(forbidNum[1])
            
            
            
            
            
                     
# KO: 
# Checked! But not tested.    
            #   Removing KOs from 'listLegal'. KOs must be added to 'listLegal' again after a move has been made. 
            #   For players who don't actually play the game, KOs are not readded to 'listLegal' after generating a move, 
            # thus self.__KO__ might be not empty and they have to be removed. 
            if self.__KO__ is not None: 
                numKO = self.moveToNum(self.__KO__)
                self.appendListLegal(numKO[1])
                self.__KO__ = None
            
            self.__KO__ = None
            for index in halfSillyIndex:
                flagRemove = False
                sillyMove = [move[0], move[1]+index[0]-1, move[2]+index[1]-1]
                if (sillyMove[1]>-1 and sillyMove[1]<self.__board__.getSize()) and (sillyMove[2]>-1 and sillyMove[2]<self.__board__.getSize()): 

                    # Checking for KO: 
                    #     This is only necessary if 'self' is about to play. 
                    #     Otherwise, is the opponent who has to take care of the KO, which wont be a KO anymore after the 
                    # opponen moves and it's "self's" turn. 
                    # Checked!! 
                    if (move[0] != self.__color__) and (actualBoard[sillyMove[1],sillyMove[2]]) == 3:
                        self.__KO__ = sillyMove
                        sillyNum = self.moveToNum(sillyMove)
                        self.popListLegal(sillyNum[1])

    
    def popListLegal(self,num): 
        """popListLegal function: 
        
            This functions checks if a number to be deleted is in 'listLegal'. If so, it's deleted. 
        
        """
        
        if num in self.__listLegal__:
            index = self.__listLegal__.index(num) 
            self.__listLegal__.pop(index)
    
    def appendListLegal(self, num):
        """appendListLegal function: 
        
            This functions appends 'num' to 'listLegal' if and only if 'num' is not in 'listLegal' yet. 
        
        """
        
        if num not in self.__listLegal__:
            self.__listLegal__.append(num)
            
    def numToMove(self, num):
        """numToMove function: 
        
            This function converts a number into a movement. 
        
        """
        
        move = [num[0]]
        move += [int(num[1]/self.__board__.getSize())]
        move += [np.mod(num[1],self.__board__.getSize())]
        return move
        
    def moveToNum(self,move):
        """moveToNum function: 
        
            This function converts a move into a number. 
        
        """
        #print 'move  = '+str(move)+'\n'
        num = [move[0], move[1]*self.__board__.getSize() + move[2]]
        return num
    
    ## Methods Keep the list of legal moves updated. 
    ##############################################################################
    
        
    
  
    

            











