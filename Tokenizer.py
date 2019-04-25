import sys
import re

whitespace = re.compile(r"\s")
fullwhitespace = re.compile(r"^\s$")

class Tokenizer:
    def __init__(self, inputFile):
        self.pos = inputFile.tell()
        self.fileReadComplete = False
        self.error = False

        self.lastToken = ""
        self.inputFile = inputFile
        self.currentLineCount = 0 #line number for error reporting
        self.currentLineIndex = 0 #location in current line
        self.currentLine = ""     #actual line stored as string
        self.reserved = ["program", "begin", "end", "int", "if", "then", "else", "while", "loop", "read", "write", "and", "or"]
        self.special = [';',',','=','!','[',']','(',')','+','-','*','!=','==','>=','<=','>','<']
    def getReservedIndex(self, check):
        #if this is a reserved word, find its index and return it
        #if it isn't a reserved word, return -1 so we can throw error
        if(check in self.reserved):
            return self.reserved.index(check) + 1
        else:
            return -1

    def getCurrentLine(self):
        return str(self.currentLineCount)
    
    def checkEndOfFile(self):
        #check if we're at the end of the file
        newpos = self.inputFile.tell()
        if newpos == self.pos:
            self.fileReadComplete = True
        else:
            self.pos = newpos

    
    def isSymbol(self,check):
        if(check in self.special):
            return True
        else:
            return False

    def getSymbolCode(self,check):
        return self.special.index(check) + 14

    def isError(self):
        return self.error

    def currentToken(self):
        return self.lastToken

    def clearWhitespace(self):
        while(whitespace.match(self.currentLine[self.currentLineIndex]) and self.currentLine[self.currentLineIndex] != "\n"):
            self.currentLineIndex += 1

    def nextToken(self):
        #if count is zero, we just began, set it to 1 and read next line
        if (self.currentLineCount == 0):
            self.currentLineCount += 1
            self.currentLine = self.inputFile.readline() + "\n"
            self.checkEndOfFile()

        #if cur index of our cur line is \n, we've reached the end of the line
        #increment line count and reset index to 0, read next line
        elif (self.currentLine[self.currentLineIndex] == "\n"):
            self.currentLineIndex = 0
            self.currentLineCount += 1
            self.currentLine = self.inputFile.readline() + "\n"
            self.checkEndOfFile()

        #Discard empty lines
        while(fullwhitespace.match(self.currentLine) and not self.fileReadComplete):
            self.currentLineIndex = 0
            self.currentLineCount += 1
            self.currentLine = self.inputFile.readline() + "\n"
            self.checkEndOfFile()

        self.currentLine = self.currentLine.lstrip() #strip off indents

        #if we've read the same line again, we're done, skip to printing 33    
        if(not self.fileReadComplete):

            #read next char to determine how to handle following chars
            nextTok = self.currentLine[self.currentLineIndex]

            if (not self.isSymbol(nextTok)): #ID, reserved, or integer

                #Retrieve the entirety of the next non-symbol token
                self.currentLineIndex += 1
                currentChar = self.currentLine[self.currentLineIndex]
                while(not whitespace.match(currentChar) and currentChar != "\n" and not self.isSymbol(currentChar)):
                    nextTok += currentChar
                    self.currentLineIndex += 1
                    currentChar = self.currentLine[self.currentLineIndex]

                if (nextTok.isnumeric()):
                    #first char is an integer
                    if(len(nextTok) > 8):
                        sys.exit("Integer Too Large" + " '" + nextTok + "'" + " - Line " + str(self.currentLineCount)+ "\n")
                    else:
                        self.lastToken = nextTok

                elif (nextTok.islower()):
                    #lowercase means reserved word, confirm this is a valid reserved word
                    if (self.getReservedIndex(nextTok) == -1):
                        sys.exit("Invalid reserved word or lowercase identifier" + " '" + nextTok + "'" + " - Line " + str(self.currentLineCount)+ "\n")
                    else:
                        self.lastToken = nextTok
                else:
                    #not lowercase, therefore this is an ID. ensure format and length of ID are valid
                    idRegEx = re.compile(r"^[A-Z]+\d*$")

                    if(len(nextTok) > 8):
                        sys.exit("ID Length Too Large" + " '" + nextTok + "'" + " - Line " + str(self.currentLineCount)+ "\n")             
                    elif (not idRegEx.match(nextTok)):
                        sys.exit("ID format invalid" + " '" + nextTok + "'" + " - Line " + str(self.currentLineCount)+ "\n")              
                    else:
                        self.lastToken = nextTok
                
            elif (self.isSymbol(nextTok)):
                #we've encountered a symbol, we need to construct the largest symbol possible
                #get next symbol, check if it produces a valid combo

                self.currentLineIndex += 1
                checkSymbol = nextTok + self.currentLine[self.currentLineIndex]

                if(self.isSymbol(checkSymbol)):
                    #This symbol exists, update global index because we will be using it
                    nextTok = checkSymbol
                    self.currentLineIndex += 1

                self.lastToken = nextTok

            #If we found whitespace, increase index until not whitespace anymore
            self.clearWhitespace()
        else:
            self.lastToken = "EOF"
