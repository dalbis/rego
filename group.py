"""Classes Group and MetaGroup: 

""" 

from copy import copy

class Group(): 
    """Stone class: 
    
    Attributes: 
        ==> color: color of the stone. 
        ==> pos: position of the stone in the board. 
        ==> lib: number of liberties of the stone. 
        ==> attS: list with the attached stones. 
        
    Methods: 
        ==> getColor, getPos, getLib, getAttS: get the corresponding attribute. 
        ==> updateLib, updateAttS: update the corresponding attribute. 
        ==> updateAttachedStones: updates '__lib__' and '__attS__' of the stones attached to self with its own liberties and the attached itself to '__attS__' of the attached stones. 
    
    """
    
    def __init__(self, color, pos): 
        """__init__ function for class Group. 
        
        """
        
        self.__color__ = color
        self.__pos__ = [pos] 
        self.__boundry__=[]  
        self.__lib__=len(self.__boundry__)
        self.__neighb__=[]
        self.__eyes__=[]
    
    def getColor(self): 
        return self.__color__
        
    def getPos(self): 
        return self.__pos__
        
    def getLib(self):
        return self.__lib__
        
    def getBoundry(self):
        return self.__boundry__
        
           
    def setBoundAndLib(self,nBoundry):
        self.__boundry__=nBoundry
        self.__lib__=len(self.__boundry__)
    
    def setPos(self,nPos):
        self.__pos__=nPos
    
    
    def addNeighb(self,NeighbGroups):
        self.__neighb__=self.__neighb__+NeighbGroups

    def delNeighb(self,Neighb):
        self.__neighb__.remove(Neighb)    

    def getNeighbours(self):
        return self.__neighb__
    
    def addEye(self,Eye):
        self.__eyes__ += [Eye]
        
    def getEye(self):
        return self.__eyes__
        

class MetaGroup(): 
    """MetaGroup class: 
    
        Objects of the class MetaGroup consist of objects of the class Group which share jointPoints. A jointPoint is defined as an empty position of the Board surrounded by four stones of the same color but not constituting an Eye. 
    
    """
    
    def __init__(self, color, listGroup, jointPoint, directKillable=None, coreGroup=None, coreGroupJP=None): 
        """__init__ function for class MetaGroup. 
        
        """
        
        # Passed variables: 
        self.__color__ = color
        self.__listGroup__ = listGroup
        self.__jointPoint__ = jointPoint
        if directKillable == None: 
            self.__directKillable__ = self.calculateDirectKillable()
        else: 
            self.__directKillable__ = directKillable
        if coreGroup == None: 
            self.__coreGroup__, self.__coreGroupJP__ = self.calculateCoreGroup()
        else: 
            self.__coreGroup__ = coreGroup
            self.__coreGroupJP__ = coreGroupJP
            
        # From here we calculate some other variables: 
        # Positions: 
        self.__pos__ = [] 
        for group in self.__listGroup__: 
            self.__pos__ += group.getPos() 
        # Core Positions: 
        self.__corePos__ = [] 
        for group in self.__coreGroup__: 
            self.__corePos__ += group.getPos() 
        # Boundary: 
        # Right now jointPoints are included in the boundry. 
        self.__boundry__ = []
        for group in self.__listGroup__: 
            for pos in group.getBoundry(): 
                if pos not in self.__boundry__: 
                    self.__boundry__ += [pos] 
        # Core Boundry: 
        self.__coreBoundry__ = []
        for group in self.__coreGroup__: 
            for pos in group.getBoundry(): 
                if pos not in self.__coreBoundry__: 
                    self.__coreBoundry__ += [pos]
                    
        # Eyes: 
        self.__eyes__ = [] 
        for group in self.__listGroup__: 
            self.__eyes__ += group.getEye() 
        self.__eyes__ += self.__coreGroupJP__
        
    def calculateDirectKillable(self): 
        """calculateDirectKillable function: 
        
        	This function calculates those Groups in self which are directly killable. A Group is directly killable if it can be killed withouth the need of killing any other Group of the MetaaGroup before. Therefore: it can not have 2 eyes; or an eye and at least a joint point; or at least two joint points. 
        
        """
        listDK = []
        for group in self.__listGroup__: 
            # It can't have 2 eyes. 
            if len(group.getEye())>1: 
                listDK += [False]
            # It can't have an eye and at least a joint point
            elif (len(group.getEye())==1): 
                for jP in self.__jointPoint__: 
                    if jP in group.getBoundry(): 
                        listDK += [False]
                        break
                        
            # It must have maximal 1 jointPoint. 
            else: 
                cJP = 0
                for jP in self.__jointPoint__: 
                    if jP in group.getBoundry(): 
                        cJP += 1
                if cJP <= 1: 
                    listDK += [True]
                else:
                    listDK += [False]
        return listDK
    
    def calculateCoreGroup(self): 
        """calculateCoreGroup function: 
        
        	This function calculates the coreGroup of self. The coreGroup consist of the maximal set of Groups of self which are unconditionally alive. We find it by sequentially removing the directly killable groups until we get a coreGroup without directly killable groups. To do so, we create the class FakeMetaGroup which extends the class MetaGroups and from which we might eliminate the directly killable Groups. 
        
        """
        
        FakeMG = MetaGroup(self.__color__, copy(self.__listGroup__), copy(self.__jointPoint__), copy(self.__directKillable__), [], [])
        flagIterate = True 
        while flagIterate: 
            nG = len(FakeMG.getGroups())
            FakeMG.removeKillable() 
            FakeMG.calculateDirectKillable()
            if len(FakeMG.getGroups()) == nG: 
                flagIterate = False
        coreGroup = [group for group in FakeMG.getGroups()] 
        coreGroupJointPoint = FakeMG.getJointPoints()
        return coreGroup, coreGroupJointPoint
        
    def removeKillable(self): 
        """removeKillable function: 
        
            This function removes those Groups from self which are directly killable. This method should not be used on MetaGroups stored in the board, it should be applied only in FakeMetaGroups created to calculate the coreGroup of a MetaGroup. 
            To remove the directly killable Groups, it first checks which Groups of self are directly killable --we can check it straightforwardly in the '__direcKillable__' variable-- and stores the index position of the groups to be removed. It then pops the groups in the positions stored before. The routine also removes the flags from '__directKillable__' in the position given before, so at the end both '__direcKillable__' and '__listGroup__' are consisten. 
            The joint points in which a removed group takes part won't be jointPoints anymore. They must also be removed. 
        
        """
        
        # Find out the groups to be removed: 
        removeList = []
        for ii in range(len(self.__listGroup__)): 
            if self.__directKillable__[ii]: 
                removeList.append(ii)
        
        # Actually remove groups and flags: 
        removeList.reverse() # We reverse this list so that we don't change the indices when removing one before the another. 
        removedGroups = [] # We need to store the removed groups in order to find the jointPoints to be erased. 
        for index in removeList: 
            self.__directKillable__.pop(index)
            removedGroups.append(self.__listGroup__.pop(index))
            
        # Finding and removing jointPoints which aren't it any longer. 
        for jP in self.__jointPoint__: 
            for group in removedGroups: 
                if jP in group.getBoundry() and jP in self.__jointPoint__: 
                    self.__jointPoint__.remove(jP)
                    
    def update(self): 
        """updateMetaGroup function: 
        
        	Recalculates all the stuff of self. 
        
        """

        self.__directKillable__ = self.calculateDirectKillable()
        self.__coreGroup__, self.__coreGroupJP__ = self.calculateCoreGroup()
            
        # Calculate some other variables: 
        # Positions: 
        self.__pos__ = [] 
        for group in self.__listGroup__: 
            self.__pos__ += group.getPos() 
        # Core Positions: 
        self.__corePos__ = [] 
        for group in self.__coreGroup__: 
            self.__corePos__ += group.getPos() 
        # Boundary: 
        # Right now jointPoints are included in the boundry. 
        self.__boundry__ = []
        for group in self.__listGroup__: 
            for pos in group.getBoundry(): 
                if pos not in self.__boundry__: 
                    self.__boundry__ += [pos] 
        # Core Boundry: 
        self.__coreBoundry__ = []
        for group in self.__coreGroup__: 
            for pos in group.getBoundry(): 
                if pos not in self.__coreBoundry__: 
                    self.__coreBoundry__ += [pos]
        # Eyes: 
        self.__eyes__ = [] 
        for group in self.__listGroup__: 
            self.__eyes__ += group.getEye() 
        self.__eyes__ += self.__coreGroupJP__


        
    def getColor(self): 
        return self.__color__
        
    def getGroups(self): 
        return self.__listGroup__
        
    def getJointPoints(self): 
        return self.__jointPoint__
        
    def getDirectKillable(self): 
        return self.__directKillable__
        
    def getCoreGroup(self): 
        return self.__coreGroup__
        
    def getCoreGroupJP(self): 
        return self.__coreGroupJP__
        
    def getPos(self): 
        return self.__pos__
    
    def getCorePos(self): 
        return self.__corePos__ 
        
    def getBoundry(self): 
        return self.__boundry__
        
    def getCoreBoundry(self): 
        return self.__coreBoundry__
        
    def getEye(self): 
        return self.__eye__

                



    