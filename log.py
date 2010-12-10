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
    
