
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


import sys,os,datetime,time,traceback

class Log:
    
    def __init__(self):
        pass
    
    def open(self):
        """
        Open the log file
        """
        self.__logFile__ = open(os.getenv("HOME")+'/log.log','w')
        self.__logFile__.write('started on '+str(datetime.datetime.fromtimestamp(time.time()))+'\n\n')
        self.__logFile__.flush()

    def close(self):
        """
        Closes the log file
        """
        self.__logFile__.close()
        
    def logException(self,e_type,e,tb):
        """
        Logs an exception
        """
        tb_list = traceback.format_exception(e_type,e,tb)
        for tb_str in tb_list:
            self.__logFile__.write(tb_str)                    
        self.__logFile__.flush()
        
    def logDebug(self,str):
        """
        Logs debug messages
        """
        self.__logFile__.write(str+'\n')
        self.__logFile__.flush()
        
    def logOutput(self,str):    
        """
        Logs the output of this engine
        """    
        self.__logFile__.write('O: '+str)
        self.__logFile__.flush()
        
    def logInput(self,str):
        """
        Logs the string received as input
        """
        self.__logFile__.write('I: '+str+'\n')
        self.__logFile__.flush()
    
