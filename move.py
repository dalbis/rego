
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

ReGo is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation either version 3 of the License, or (at your option) any later version. 

ReGo is distributed with the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License in file COPYING for more details. 

You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/>. 

"""


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
