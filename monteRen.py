
import move as M
from board import Board
from copy import copy
from player import Player
from numpy import random
import numpy as np
import random as iran

# **** function updateBoard
def __updateBoard__(movPos,movColor,bData):

    boardSize = len(bData)
    boardProbs=np.zeros([boardSize,boardSize])

    x=movPos[0]
    y=movPos[1]

    # update stone colors and counts on the renormalized board
    empCount=bData[x][y][1]  
    bCount=bData[x][y][2]  
    wCount=bData[x][y][3]  
    posColor=bData[x][y][0]

    if movColor is 'b':
        bCount=bCount+1
    else:
        wCount=wCount+1
    empCount=empCount-1

    bData[x][y][1]=empCount 
    bData[x][y][2]=bCount 
    bData[x][y][3]=wCount  

    if bCount == 0 and wCount == 0:
        newPosColor = 0
    elif bCount >= wCount:     # maybe later note this? biased toward balck?
        newPosColor = 1
    elif bCount < wCount:
        newPosColor = 2

    bData[x][y][0]=newPosColor

    # update playable positions and probabilities
    playList=[]
    for x in xrange(boardSize):
        for y in xrange(boardSize):

            empCount=bData[x][y][1]  
            bCount=bData[x][y][2]  
            wCount=bData[x][y][3]  
            if empCount>0:
                playList.append([x,y])

            boardProbs[x,y]=np.exp(min([bCount,wCount])-max([bCount,wCount]))
    #print sum(nc)
    return [bData,playList,boardProbs]

# **** function evaluate
def evaluate(bData):
    stoneColors=np.array([bData[i][j][0] for i in xrange(len(bData)) for j in xrange(len(bData))])
    nB=sum(stoneColors==1)
    nW=sum(stoneColors==2)

    if nB>nW:
        return 'Black'
    elif nB<nW:
        return 'White'
    else:
        return iran.choice(['Black','White'])
# *** 

def mycopy(a):
    b = [[[e for e in el] for el in row] for row in a ]
    return b
    

def MonteCarloRen(renBoardData,ourColor,wsize):   # RenBoardData Format: [color,numEmpty,bCount,wCount]  maybe we need to use numEmpty later

    numRuns = 5;
    movesPerRun = 10;
    
    lettList=['A','B','C','D','E','F','G','H','J','K','L','M','N','O','P','Q','R','S','T']
    
    boardSize=len(renBoardData)

    playablePosList=[]    # List of posisions in the ren board that have empty spaces in the original board
    
    # Filling playable postitions and calculating the probability of playing in positions of the Renormalized board.
    alEmps=[]
    for x in xrange(boardSize):
        for y in xrange(boardSize):

            empCount=renBoardData[x][y][1]
            alEmps.append(empCount)
            if empCount>0:
                playablePosList.append([x,y])
    totalEmps=sum(alEmps)
    movesPerRun=10 if totalEmps>10 else totalEmps

    # play using monte carlo
    
    if ourColor=='b':
       oppColor='w'
    else:
       oppColor='b'

    winProbList=[]


    for pos in playablePosList:  
        
        tryWinList=[]

        for run in range(numRuns):


            boardData=mycopy(renBoardData)

            # we play in pos and then we start montecarlo to evaluate the board at the end 
            [boardData,playList,boardProbs]=__updateBoard__(pos,ourColor,boardData)
            numPos=len(playList)

            for moves in range(movesPerRun):

                # finding a move for opponent the prob of which is more than a random number
                oppPlayCandidate=playList[random.randint(numPos)]
                while boardProbs[oppPlayCandidate[0],oppPlayCandidate[1]]<random.random():
                    oppPlayCandidate=playList[random.randint(numPos)]

                [boardData,playList,boardProbs]=__updateBoard__(oppPlayCandidate,oppColor,boardData)
                numPos=len(playList)


                # finding a move for ourselves the prob of which is more than a random number
                ourPlayCandidate=playList[random.randint(numPos)]
                while boardProbs[ourPlayCandidate[0],ourPlayCandidate[1]]<random.random():
                    ourPlayCandidate=playList[random.randint(numPos)]

                [boardData,playList,boardProbs]=__updateBoard__(ourPlayCandidate,ourColor,boardData)
                numPos=len(playList)

            # end of monte moves

            # playing one more for opponent because we started first
            oppPlayCandidate=playList[random.randint(numPos)]
            while boardProbs[oppPlayCandidate[0],oppPlayCandidate[1]]<random.random():
                oppPlayCandidate=playList[random.randint(numPos)]

            [boardData,playList,boardProbs]=__updateBoard__(ourPlayCandidate,ourColor,boardData)
            numPos=len(playList)


            tryWinList.append(evaluate(boardData))

        # calculate position probability and append it
        numB=tryWinList.count('Black')   
        numW=tryWinList.count('White')
        if ourColor=='b':
            prob=float(numB)/(numB+numW)
        else:
            prob=float(numW)/(numB+numW)
        winProbList.append(prob)

    maxValue = max(winProbList)
    winProbList = np.array(winProbList)
    maxIdxs = np.where( winProbList == maxValue)[0]
    maxIndex = iran.choice(maxIdxs)

    ourPlayX= playablePosList[maxIndex][0]
    ourPlayY= playablePosList[maxIndex][1]
    
    # we found the position in the normalized board, now we return the cluster in the original board
    X=[ourPlayX*wsize+i for i in xrange(wsize)]   # left up corner of the chosen cluster
    Y=[ourPlayY*wsize+i for i in xrange(wsize)]


    origBoardSize=19 # change it later
    cluster=[x*origBoardSize+y for x in X for y in Y]  

    #print cluster
    return cluster



