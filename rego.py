#!/usr/bin/python

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

from board import Board
from player import Player
from move import Move
from group import Group
from log import Log
from monte import MonteCarlo

import sys

class SyntaxError(Exception):
    """
    This exception must be raised when the input contains a syntax error
    """
    pass

class ConsistencyError(Exception):
    """
    This exception must be raised when there is a consistency error: e.g. the same move is given twice
    """
    pass

class ReGo:
    
    def __init__(self):
        """
        Constructor of the class ReGo
        """
    
        # known commands
        self.knownCmds = [ 'protocol_version' , 'name' , 'version' , 'known_command' , 'list_commands' ,'quit' , 'boardsize' , 'clear_board' , 'komi' , 'play' , 'genmove' ]
        
        # open log
        self.log = Log()
        self.log.open()
        
        # board
        self.board = Board(19,self.log)
        
        # score
        self.score = 0.0
        
        # players
        self.bPlayer = Player('b',self.board,self.log)
        self.wPlayer = Player('w',self.board,self.log)    
        
    
    
    def __decodeLine__(self,line):
        """
        Decodes an input line read from stdin
        """
        vals = line.split(' ')
        return (vals[0],vals[1:])
    
    def __decodeColor__(self,colorStr):
        """
        Decodes a color string
        """
        if colorStr.upper() in ('B','BLACK'):
            return 'b'
            
        elif colorStr.upper() in ('W','WHITE'):
            return 'w'
        else:
            raise SyntaxError('illegal color')
    
    def __decodePosition__(self,posStr):
        """
        Decodes a position string
        """
        try:
            posLetter = posStr[0].upper()
            posNumber = int(posStr[1:])
        except Exception:
            raise SyntaxError('invalid position')
        else:
            return posLetter,posNumber
    
    def __handleError__(self):
        """
        Checks for the exception raised and returns the error string. It logs also the exception stack-trace in case of an unexpected error.
        """
        e_type, e, tb = sys.exc_info()
        
        # syntax error
        if e_type == SyntaxError:
            output_line = '? syntax error: '+e.message+'\n\n'
        
        # consistency error
        elif e_type == ConsistencyError:
            output_line = '? consistency error: '+e.message+'\n\n'

        # unexpected error
        else:
            output_line = '? unexpected error\n\n'
            self.log.logException(e_type, e, tb )
            
        return output_line
        
    def protocol_version(self,args):
        """
        Prints GTP protocol version
        """
        return '2'
    
    def name(self,args):
        """
        Prints the name of this GO engine
        """
        return 'Rego'
    
    def version(self,args):
        """
        Prints the version of this GO engine
        """
        return '0.1'
    
    def know_command(self,args):
        """
        Returns true if the command specified is known, false otherwise
        """
        if not args[0]:
            raise SyntaxError('invalid command name')
        
        if args[0] in self.knownCmds:
            return 'true'
        else:
            return 'false'    
           
    def list_commands(self,args):
        """
        Lists known commands
        """
        return ' '.join(self.knownCmds)
    
    def boardsize(self,args):
        """
        Set the new board size to the number specified by the argument
        """
        try:
            size = int(args[0])
        except Exception:
            raise SyntaxError('board size is not an integer')
        else:
            self.board = Board(int(args[0]),self.log)
            return ''
    
    def clear_board(self,args):
        """
        Clears the board
        """
        self.board.clear()
        self.bPlayer = Player('b',self.board,self.log)
        self.wPlayer = Player('w',self.board,self.log) 
        return ''
    
    def komi(self,args):
        """
        Sets the new komi to the float value specified as argument
        """
        try:
            komi = float(args[0])
        except Exception:
            raise SyntaxError('komi is not a float')
        else:
            self.score = float(args[0])
            return ''
    
    def play(self,args):
        """
        Updates the board according to the move specified as argument
        """
        color = self.__decodeColor__(args[0])
        posLetter,posNumber = self.__decodePosition__(args[1])
    
        m = Move(color=color,posLetter=posLetter,posNumber=posNumber)
        
        self.board.update(m)

        self.bPlayer.updateListLegal(m.getListFormat(),self.board.getKilled())
        self.wPlayer.updateListLegal(m.getListFormat(),self.board.getKilled())
        
        self.log.logDebug(self.board.showBoard())
                
        return ''
    
    def genmove(self,args):
        """
        Generate a new move for the player specified as argument
        """
        
        
        move = MonteCarlo(self.log,self.board, self.__decodeColor__(args[0]), self.bPlayer, self.wPlayer)
        
        self.board.update(move)     
        
        self.bPlayer.updateListLegal(move.getListFormat(),self.board.getKilled())
        self.wPlayer.updateListLegal(move.getListFormat(),self.board.getKilled())
        
        self.log.logDebug(self.board.showBoard())

        return move.encode()
    
    
    def execute(self):
        """
        Main method: reads a command from stdin and writes the output to stdout
        
        """
        
        # read first input
        line = raw_input()
        self.log.logInput(line)
        cmd, args = self.__decodeLine__(line)

        # main loop
        while not cmd == 'quit':
    
            if cmd in self.knownCmds:
                method = getattr(self,cmd)
            
                try:    
                    output = method(args)
                except Exception:
                    output_line = self.__handleError__()
                    
                else:
                    output_line = '= '+output+'\n\n'
        
            else:
                output_line  = '? unknown command\n\n'
            

            # write back the output line to stdout
            sys.stdout.write(output_line)
            sys.stdout.flush()
                        
            # log the output            
            self.log.logOutput(output_line)
            
            # read the next input
            line = raw_input()
            self.log.logInput(line)
            cmd, args = self.__decodeLine__(line)
        
        self.log.close()

if __name__ == '__main__':
    rego = ReGo()
    rego.execute()

    # This is for profiling the code:
	#import profile
    #profile.run("rego.genmove('b')")
