
import move as M
from board import Board
from copy import copy
from player import Player
import monteRen as mR
import random as iran
import numpy as np

def MonteCarlo(log,board,ourColor,Bplayer,Wplayer):
    
    numRuns = 5;
    movesPerRun = 10;
    
    lettList=['A','B','C','D','E','F','G','H','J','K','L','M','N','O','P','Q','R','S','T']
    
    
    BListLegal=Bplayer.getListLegal()
    WListLegal=Wplayer.getListLegal()
   
    if ourColor == "b": 
        ListLegal=BListLegal
    else: 
        ListLegal=WListLegal 

    # renormalize the board and get the chosen cluster. Then we will choose within the cluster using MonteCarlo
    renBoard=board.renormalize()
    cluster=mR.MonteCarloRen(renBoard,ourColor,2)

    movesToCheck=[p for p in cluster if p in ListLegal]


    winProbList=[]
    for p in movesToCheck:
        
        tryWinList=[]
        for do in range(numRuns):
            """Initial values  """        
            virBoard=board.copy()
            
            ourPlayer=Player(ourColor,virBoard,ListLegal)
            if ourColor=="b": 
                oppPlayer=Player('w',virBoard,WListLegal)
            else:
                oppPlayer=Player('b',virBoard,BListLegal)
        
	        # our player play first
            move=ourPlayer.numToMove([ourColor,p])
            moveObject = M.Move(posLetter=lettList[move[2]], posNumber=19-move[1],color=move[0])  
            virBoard.update(moveObject)
            ourPlayer.updateListLegal(move, virBoard.getKilled())   ### insult
            oppPlayer.updateListLegal(move, virBoard.getKilled())   ### insult
            ourListLegal=ourPlayer.getListLegal()
            oppListLegal=oppPlayer.getListLegal()

            # Playing randomly with two slave players on a pseudo board
            moveNum = 0
            while (ourListLegal!=[] and oppListLegal!=[]) and moveNum < movesPerRun:

                # gen move for opponent
                move=oppPlayer.genMove()
                if move!=None:
                    virBoard.update(move)     
                    ourPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                    oppPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                    ourListLegal=ourPlayer.getListLegal()
                    oppListLegal=oppPlayer.getListLegal()
 
               # gen move for us
                move=ourPlayer.genMove()
                if move!=None:
                    virBoard.update(move)     
                    ourPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                    oppPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                    ourListLegal=ourPlayer.getListLegal()
                    oppListLegal=oppPlayer.getListLegal()

                moveNum+=1

            # end of the while

            # gen move for opponent
            move=oppPlayer.genMove()
            if move!=None:
                virBoard.update(move)     
                ourPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                oppPlayer.updateListLegal(move.getListFormat(),virBoard.getKilled())
                ourListLegal=ourPlayer.getListLegal()
                oppListLegal=oppPlayer.getListLegal()

            BListLegal=Bplayer.getListLegal()
            WListLegal=Wplayer.getListLegal()

            tryWinList.append(virBoard.evaluate())
            #print 'completed run ',do,'/',numRuns-1
            
        # end of runs
        
        numB=tryWinList.count('Black')   
        numW=tryWinList.count('White')

        if ourColor=='b':
            prob=float(numB)/(numB+numW)
        else:
            prob=float(numW)/(numB+numW)

        winProbList.append(prob)
        #print 'completed evaluation of position ',ListLegal.index(p),'/',len(ListLegal)-1
        
    # end of evaluation of move p
    #print winProbList

    maxValue = max(winProbList)
    winProbList = np.array(winProbList)
    maxIdxs = np.where( winProbList == maxValue)[0]
    maxIndex = iran.choice(maxIdxs)

    #print maxIndex

    #max_index=winProbList.index(max(winProbList))   # improve this if more than one max 
    move=ourPlayer.numToMove([ourColor, movesToCheck[maxIndex]])
    
    #print 'winProbList: ',winProbList
    #print 'best move: ',move
    return M.Move(posLetter=lettList[move[2]], posNumber=19-move[1],color=move[0])    
 
      
     



     
     

 
