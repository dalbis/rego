
class Move:
        
    def __init__(self,posLetter = None, posNumber = None, color = None):

        if posLetter and posNumber and color:
            self.__posLetter__ = posLetter
            self.__posNumber__ = posNumber
            self.__color__ = color
            
    def encode(self):
        return self.__posLetter__+str(self.__posNumber__)

    def getPosLetter(self):
        return self.__posLetter__

    def getPosNumber(self):
        return self.__posNumber__

    def getColor(self):
        return self.__color__
    
    def getListFormat(self):
        """
        Returns the move as a list format, e.g.  ['b', 2, 13]
        """
        alphabet='ABCDEFGHJKLMNOPQRST'        
        row=19-self.getPosNumber()
        col=alphabet.find(self.getPosLetter())
        return [self.getColor(),row,col]
