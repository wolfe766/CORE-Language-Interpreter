from Tokenizer import Tokenizer
import sys

class Prog:
    def __init__(self):
        self.declSeq = ""
        self.stmtSeq = ""
    
    def parseProg(self, tokenizer):
        matchAndConsume(tokenizer, "program")
        self.declSeq = declSeq()
        self.declSeq.parseDeclSeq(tokenizer)
        matchAndConsume(tokenizer, "begin")
        self.stmtSeq = stmtSeq()
        self.stmtSeq.parseStmtSeq(tokenizer)
        matchAndConsume(tokenizer, "end")
        matchAndConsume(tokenizer,"EOF")
    
    def printProg(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # program
        tokenizer.nextToken()
        string = printAndClearString(string)

        indentLevel += 1
        self.declSeq = declSeq()
        string = self.declSeq.printDeclSeq(tokenizer, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # begin
        tokenizer.nextToken() 

        string = printAndClearString(string)       
        
        indentLevel += 1
        self.stmtSeq = stmtSeq()
        string = self.stmtSeq.printStmtSeq(tokenizer, string, indentLevel)
        indentLevel -= 1

        string = addToString(tokenizer.currentToken(), string, indentLevel) # end
        tokenizer.nextToken()
        string = printAndClearString(string)    

    def execProg(self):
        self.declSeq.execDeclSeq()
        self.stmtSeq.execStmtSeq()

class declSeq:
    def __init__(self):
        self.declSeq = ""
        self.decl = ""
    
    def parseDeclSeq(self, tokenizer):
        self.decl = decl()
        self.decl.parseDecl(tokenizer)
        if(tokenizer.currentToken() == "int"):
            self.declSeq = declSeq()
            self.declSeq.parseDeclSeq(tokenizer)

    def printDeclSeq(self, tokenizer, string, indentLevel):
        self.decl = decl()
        string = self.decl.printDecl(tokenizer, string, indentLevel)

        if(tokenizer.currentToken() == "int"):
            self.declSeq = declSeq()
            string = self.declSeq.printDeclSeq(tokenizer, string, indentLevel)
        
        return string

    def execDeclSeq(self):
        self.decl.execDecl()
        if(self.declSeq != ""):
            self.declSeq.execDeclSeq()

class stmtSeq:
    def __init__(self):
        self.stmts = []
        self.stmtCount = -1
    
    def parseStmtSeq(self, tokenizer):
        #Keep parsing statements until we reach an "end" or an "else"
        while(tokenizer.currentToken() != "end" and tokenizer.currentToken() != "else"):
            self.stmts.append(stmt())
            self.stmtCount += 1
            self.stmts[self.stmtCount].parseStmt(tokenizer)

    def printStmtSeq(self, tokenizer, string, indentLevel):
        #Keep printing until we reach an "end" or an "else"
        while(tokenizer.currentToken() != "end" and tokenizer.currentToken() != "else"):
            self.stmt = stmt()
            string = self.stmt.printStmt(tokenizer, string, indentLevel)
    
        return string

    def execStmtSeq(self):
        for stmt in self.stmts:
            stmt.execStmt()
class decl:
    def __init__(self):
        self.idList = ""
    
    def parseDecl(self, tokenizer):
        matchAndConsume(tokenizer, "int")
        self.idList = idList()
        self.idList.parseIdList(tokenizer, True)
        matchAndConsume(tokenizer,";")

    def printDecl(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # int
        tokenizer.nextToken()

        self.idList = idList()
        string = self.idList.printIdList(tokenizer, True, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # ;
        tokenizer.nextToken()

        string = printAndClearString(string)

        return string

    def execDecl(self):
        i = 0
        #do nothing, declarations are handled by the parser

class idList:
    def __init__(self):
        self.ids = []
        self.idCount = 0

    def parseIdList(self, tokenizer, declaring):
        self.ids.append(idClass())
        self.ids[self.idCount].parseId(tokenizer, declaring)
        self.idCount += 1

        #If current token is a comma, there is another ID to parse
        while(tokenizer.currentToken() == ","):
            tokenizer.nextToken()
            self.ids.append(idClass())
            self.ids[self.idCount].parseId(tokenizer, declaring)
            self.idCount += 1

    def printIdList(self, tokenizer, declaring, string, indentLevel):
        self.id = idClass()
        string = self.id.printId(tokenizer, declaring, string, indentLevel)

        #If current token is a comma, there is another ID to print
        while(tokenizer.currentToken() == ","):
            string = addToString(tokenizer.currentToken(), string, indentLevel) # ,
            tokenizer.nextToken()
            string = self.id.printId(tokenizer, declaring, string, indentLevel)

        return string
        
    def getIds(self):
        return self.ids

class idClass:
    def __init__(self):
        self.isDeclared = False
        self.symbol = ""

    def parseId(self, tokenizer, declaring):
        if(tokenizer.currentToken() not in symbolTable):
            #If ID is not in the symbol table and they aren't declaring it, there is an error
            if(declaring == False): 
                #If it is obviously not an ID, notify them of that error
                if(not tokenizer.currentToken().isalpha()):
                    sys.exit("ERROR - Invalid Identifier '" + tokenizer.currentToken() + "' - Line " + tokenizer.getCurrentLine())
                #If it could be an ID (all alpha characters) inform them it is not delcared
                else:
                    sys.exit("ERROR - Identifier not declared '" + tokenizer.currentToken() + "' - Line " + tokenizer.getCurrentLine())
            else:
                #If they're declaring it, add it to the symbol table
                symbolTable[tokenizer.currentToken()] = "null"
                self.symbol = tokenizer.currentToken()
                tokenizer.nextToken()
        #If it IS in the symbol table and they're declaring it, thats an error
        elif (declaring == True):
            sys.exit("ERROR - Identifier already declared '" + tokenizer.currentToken() + "' - Line " + tokenizer.getCurrentLine())
        else:
            self.symbol = tokenizer.currentToken()
            tokenizer.nextToken()

    def printId(self, tokenizer, declaring, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # ID
        tokenizer.nextToken()

        return string

    def getSymbol(self):
        return self.symbol

class stmt:
    def __init__(self):
        self.assign = ""
        self.ifStmt = ""
        self.loop = ""
        self.inStmt = ""
        self.outStmt = ""
        self.alt = 0
    
    def parseStmt(self, tokenizer):
        tok = tokenizer.currentToken()

        if(tok == "write"):
            self.outStmt = outStmt()
            self.outStmt.parseOut(tokenizer)
            self.alt = 5
        elif(tok == "read"):
            self.inStmt = inStmt()
            self.inStmt.parseIn(tokenizer)
            self.alt = 4
        elif(tok == "if"):
            self.ifStmt = ifStmt()
            self.ifStmt.parseIf(tokenizer)
            self.alt = 2
        elif(tok == "while"):
            self.loop = loop()
            self.loop.parseLoop(tokenizer)
            self.alt = 3
        else:
            self.assign = assign()
            self.assign.parseAssign(tokenizer)
            self.alt = 1

    def printStmt(self, tokenizer, string, indentLevel):
        tok = tokenizer.currentToken()

        if(tok == "write"):
            self.outStmt = outStmt()
            string = self.outStmt.printOut(tokenizer, string, indentLevel)
        elif(tok == "read"):
            self.inStmt = inStmt()
            string = self.inStmt.printIn(tokenizer, string, indentLevel)
        elif(tok == "if"):
            self.ifStmt = ifStmt()
            string = self.ifStmt.printIf(tokenizer, string, indentLevel)
        elif(tok == "while"):
            self.loop = loop()
            string = self.loop.printLoop(tokenizer, string, indentLevel)
        else:
            self.assign = assign()
            string = self.assign.printAssign(tokenizer, string, indentLevel)

        return string

    def execStmt(self):
        if(self.alt == 1):
            self.assign.execAssign()
        elif(self.alt == 2):
            self.ifStmt.execIf()
        elif(self.alt == 3):
            self.loop.execLoop()
        elif(self.alt == 4):
            self.inStmt.execRead()
        elif(self.alt == 5):
            self.outStmt.execWrite()
        else:
            print("ERROR? Statemnt not recognized")

class assign:
    def __init__(self):
        self.id = ""
        self.expr = ""
    
    def parseAssign(self, tokenizer):
        self.id = idClass()
        self.id.parseId(tokenizer, False)
        matchAndConsume(tokenizer, "=")
        self.expr = expr()
        self.expr.parseExpr(tokenizer)
        matchAndConsume(tokenizer,";")

    def printAssign(self, tokenizer, string, indentLevel):
        self.id = idClass()
        string = self.id.printId(tokenizer, False, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # =
        tokenizer.nextToken()

        self.expr = expr()
        string = self.expr.printExpr(tokenizer, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # ;
        tokenizer.nextToken()

        string = printAndClearString(string)

        return string

    def execAssign(self):
        curId = self.id.getSymbol()
        curVal = self.expr.evalExpr()
        symbolTable[curId] = curVal

class ifStmt:
    def __init__(self):
        self.cond= ""
        self.stmtSeqOne = ""
        self.stmtSeqTwo = ""
        self.alt = 0
    
    def parseIf(self, tokenizer):
        matchAndConsume(tokenizer, "if")
        self.cond = cond()
        self.cond.parseCond(tokenizer)
        matchAndConsume(tokenizer, "then")
        self.stmtSeqOne = stmtSeq()
        self.stmtSeqOne.parseStmtSeq(tokenizer)

        #If there is an else, parse it
        if(tokenizer.currentToken() == "else"):
            matchAndConsume(tokenizer, "else")
            self.stmtSeqTwo = stmtSeq()
            self.stmtSeqTwo.parseStmtSeq(tokenizer)
            self.alt = 2
        else:
            self.alt = 1

        matchAndConsume(tokenizer, "end")
        matchAndConsume(tokenizer, ";")

    def printIf(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) #if
        tokenizer.nextToken()

        self.cond = cond()
        string = self.cond.printCond(tokenizer, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) #then
        tokenizer.nextToken()

        string = printAndClearString(string)

        #Indent and print the statement sequence in the if block
        indentLevel += 1
        self.stmtSeqOne = stmtSeq()
        string = self.stmtSeqOne.printStmtSeq(tokenizer, string, indentLevel)
        indentLevel -= 1

        #If there is an else, indent and print the statement sequence
        if(tokenizer.currentToken() == "else"):
            string = addToString(tokenizer.currentToken(), string, indentLevel) #else
            tokenizer.nextToken()

            string = printAndClearString(string)

            indentLevel += 1
            self.stmtSeqTwo = stmtSeq()
            string = self.stmtSeqTwo.printStmtSeq(tokenizer, string, indentLevel)
            indentLevel -= 1

            string = addToString(tokenizer.currentToken(), string, indentLevel) #end
            tokenizer.nextToken()

            string = addToString(tokenizer.currentToken(), string, indentLevel) #;
            tokenizer.nextToken()

            string = printAndClearString(string)

        return string

    def execIf(self):
        condResult = self.cond.evalCond()
        if(condResult == True):
            self.stmtSeqOne.execStmtSeq()
        elif(self.alt == 2):
            self.stmtSeqTwo.execStmtSeq()
    
class loop:
    def __init__(self):
        self.cond =  ""
        self.stmtSeq = ""
    
    def parseLoop(self, tokenizer):
        matchAndConsume(tokenizer, "while")
        self.cond = cond()
        self.cond.parseCond(tokenizer)
        matchAndConsume(tokenizer, "loop")
        self.stmtSeq = stmtSeq()
        self.stmtSeq.parseStmtSeq(tokenizer)
        matchAndConsume(tokenizer, "end")
        matchAndConsume(tokenizer, ";")

    def printLoop(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # while
        tokenizer.nextToken()

        self.cond = cond()
        string = self.cond.printCond(tokenizer, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # loop
        tokenizer.nextToken()
        string = printAndClearString(string)

        indentLevel += 1
        self.stmtSeq = stmtSeq()
        string = self.stmtSeq.printStmtSeq(tokenizer, string, indentLevel)
        indentLevel -= 1

        string = addToString(tokenizer.currentToken(), string, indentLevel) #end
        tokenizer.nextToken()

        string = addToString(tokenizer.currentToken(), string, indentLevel) # ;
        tokenizer.nextToken()
        string = printAndClearString(string)

        return string

    def execLoop(self):
        condVal = self.cond.evalCond()
        while(condVal == True):
            self.stmtSeq.execStmtSeq()
            condVal = self.cond.evalCond()

class inStmt:
    def __init__(self):
        self.idList = idList()
    
    def parseIn(self, tokenizer):
        matchAndConsume(tokenizer, "read")
        self.idList.parseIdList(tokenizer, False)
        matchAndConsume(tokenizer, ";")

    def printIn(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # Read
        tokenizer.nextToken()

        string = self.idList.printIdList(tokenizer, False, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # ;
        tokenizer.nextToken()

        string = printAndClearString(string)

        return string

    def execRead(self):
        ids = self.idList.getIds()
        userInput = "null"
        for curId in ids:
            userInput = input(curId.getSymbol() + " =? ")
            
            if(not userInput.isnumeric()):
                sys.exit("ERROR: Input must be an integer")

            #Do not need to handle overly large integers here because
            #Python supports arbitrarily large integers

            symbolTable[curId.getSymbol()] = int(userInput)

class outStmt:
    def __init__(self):
        self.idList = idList()

    def parseOut(self, tokenizer):
        matchAndConsume(tokenizer, "write")
        self.idList.parseIdList(tokenizer, False)
        matchAndConsume(tokenizer, ";")

    def printOut(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # Write
        tokenizer.nextToken()

        string = self.idList.printIdList(tokenizer, False, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # ;
        tokenizer.nextToken()

        string = printAndClearString(string)

        return string

    def execWrite(self):
        ids = self.idList.getIds()
        for curId in ids:
            print(curId.getSymbol() + " = " + str(getIdValue(curId)))
class cond:
    def __init__(self):
        self.comp = ""
        self.cond = ""
        self.condTwo = ""
        self.alt = 0

    def parseCond(self, tokenizer):
        if(tokenizer.currentToken() == "!"):
            matchAndConsume(tokenizer, "!")
            self.cond = cond()
            self.cond.parseCond(tokenizer)
            self.alt = 2
        elif(tokenizer.currentToken() == "["):
            matchAndConsume(tokenizer, "[")
            self.cond = cond()
            self.cond.parseCond(tokenizer)

            #Make sure that the operator is valid
            op = tokenizer.currentToken()
            if(op == "and"):
                self.alt = 3
            elif(op == "or"):
                self.alt = 4
            else:
                sys.exit("ERROR - expected 'and' or 'or' in condition" + " - Line " + tokenizer.getCurrentLine())

            #Consume the operator
            tokenizer.nextToken()
            self.condTwo = cond()
            self.condTwo.parseCond(tokenizer)

            matchAndConsume(tokenizer, "]")
        else:
            self.comp = comp()
            self.comp.parseComp(tokenizer)
            self.alt = 1

    def printCond(self, tokenizer, string, indentLevel):
        if(tokenizer.currentToken() == "!"):
            string = addToString(tokenizer.currentToken(), string, indentLevel) # !
            tokenizer.nextToken()

            self.cond = cond()
            string = self.cond.printCond(tokenizer, string, indentLevel)
        elif(tokenizer.currentToken() == "["):
            string = addToString(tokenizer.currentToken(), string, indentLevel) # [
            tokenizer.nextToken()

            self.cond = cond()
            string = self.cond.printCond(tokenizer, string, indentLevel)

            #Consume the operator
            string = addToString(tokenizer.currentToken(), string, indentLevel) # AND or OR
            tokenizer.nextToken()

            self.condTwo = cond()
            string = self.condTwo.printCond(tokenizer, string, indentLevel)

            string = addToString(tokenizer.currentToken(), string, indentLevel) # ]
            tokenizer.nextToken()
        else:
            self.comp = comp()
            string = self.comp.printComp(tokenizer, string, indentLevel)

        return string

    def evalCond(self):
        result = "null"
        if(self.alt == 1):
            result = self.comp.evalComp()
        elif(self.alt == 2):
            result = not self.cond.evalCond()
        elif(self.alt == 3):
            result = (self.cond.evalCond() and self.condTwo.evalCond())
        elif(self.alt == 4):
            result = (self.cond.evalCond() or self.condTwo.evalCond())
        else:
            print("ERROR - Condition invalid?")

        return result

class comp:
    def __init__(self):
        self.facOne = ""
        self.facTwo = ""
        self.compOp = ""
    def parseComp(self, tokenizer):
        matchAndConsume(tokenizer, "(")
        self.facOne = fac()
        self.facOne.parseFac(tokenizer)

        #Check valid comp operator, if not in this list, error
        compops = ["!=","==","<",">","<=",">="]
        if(tokenizer.currentToken() not in compops):
            sys.exit("ERROR - Comparison operator '" + tokenizer.currentToken() + "' not recognized" + " - Line " + tokenizer.getCurrentLine())
        else:
            self.compOp = tokenizer.currentToken()
            tokenizer.nextToken()
            self.facTwo = fac()
            self.facTwo.parseFac(tokenizer)

        matchAndConsume(tokenizer, ")")

    def printComp(self, tokenizer, string, indentLevel):
        string = addToString(tokenizer.currentToken(), string, indentLevel) # (
        tokenizer.nextToken()

        self.facOne = fac()
        string = self.facOne.printFac(tokenizer, string, indentLevel)

        string = addToString(tokenizer.currentToken(), string, indentLevel) # Operator
        tokenizer.nextToken()

        self.facTwo = fac()
        string = self.facTwo.printFac(tokenizer, string, indentLevel) 

        string = addToString(tokenizer.currentToken(), string, indentLevel) # )
        tokenizer.nextToken()

        return string

    def evalComp(self):
        facOneVal = self.facOne.evalFac()
        facTwoVal = self.facTwo.evalFac()
        result = "null"

        if(self.compOp == "!="):
            result = (facOneVal != facTwoVal)
        elif(self.compOp == "=="):
            result = (facOneVal == facTwoVal)
        elif(self.compOp == "<="):
            result = (facOneVal <= facTwoVal)
        elif(self.compOp == ">="):
            result = (facOneVal >= facTwoVal)
        elif(self.compOp == "<"):
            result = (facOneVal < facTwoVal)
        elif(self.compOp == ">"):
            result = (facOneVal > facTwoVal)
        else:
            print("ERROR - Operator not recognized?")
        
        return result
class expr:
    def __init__(self):
        self.term = ""
        self.expr = ""
        self.alt = 0

    def parseExpr(self, tokenizer):
        self.term = term()
        self.term.parseTerm(tokenizer)

        if(tokenizer.currentToken() == "+"):
            matchAndConsume(tokenizer, "+")
            self.expr = expr()
            self.expr.parseExpr(tokenizer)
            self.alt = 2
        elif(tokenizer.currentToken() == "-"):
            matchAndConsume(tokenizer, "-")
            self.expr = expr()
            self.expr.parseExpr(tokenizer)
            self.alt = 3
        else:
            self.alt = 1

    def printExpr(self, tokenizer, string, indentLevel):
        self.term = term()
        string = self.term.printTerm(tokenizer, string, indentLevel)

        if(tokenizer.currentToken() == "+" or tokenizer.currentToken() == "-"):
            string = addToString(tokenizer.currentToken(), string, indentLevel)
            tokenizer.nextToken()
            self.expr = expr()
            string = self.expr.printExpr(tokenizer, string, indentLevel)

        return string

    def evalExpr(self):
        result = "null"
        termVal = self.term.evalTerm()

        if(self.alt == 1):
            result = termVal
        elif(self.alt == 2):
            result = termVal + self.expr.evalExpr()
        elif(self.alt == 3):
            result = termVal - self.expr.evalExpr()

        return result

class term:
    def __init__(self):
        self.fac = ""
        self.term = ""
        self.alt = 0

    def parseTerm(self, tokenizer):
        #Get the first factor
        self.fac = fac()
        self.fac.parseFac(tokenizer)
        
        #If next tok is *, its alt 2
        if(tokenizer.currentToken() == "*"):
            matchAndConsume(tokenizer, "*")
            self.term = term()
            self.term.parseTerm(tokenizer)
            self.alt = 2
        else:
            self.alt = 1

    def printTerm(self, tokenizer, string, indentLevel):
        self.fac = fac()
        string = self.fac.printFac(tokenizer, string, indentLevel)
        
        if(tokenizer.currentToken() == "*"):
            string = addToString(tokenizer.currentToken(), string, indentLevel)
            tokenizer.nextToken()
            self.term = term()
            string = self.term.printTerm(tokenizer, string, indentLevel)

        return string
        
    def evalTerm(self):
        facVal = self.fac.evalFac()
        result = "null"

        if(self.alt == 1):
            result = facVal
        elif(self.alt == 2):
            result = facVal * self.term.evalTerm()
        
        return result

class fac:    
    def __init__(self):
        self.expr = ""
        self.id = ""
        self.int = ""
        self.alt = 0

    def parseFac(self, tokenizer):
        #If its a number, parse it
        if(tokenizer.currentToken().isdigit()):
            self.int = int(tokenizer.currentToken())
            tokenizer.nextToken()
            self.alt = 1
        elif(tokenizer.currentToken() != "("):
            self.id = idClass()
            self.id.parseId(tokenizer, False)
            self.alt = 2
        else:
            #Parse the expression
            matchAndConsume(tokenizer, "(")
            self.expr = expr()
            self.expr.parseExpr(tokenizer)
            self.alt = 3
            matchAndConsume(tokenizer, ")")

    def printFac(self, tokenizer, string, indentLevel):
        if(tokenizer.currentToken().isdigit()):
            string = addToString(tokenizer.currentToken(), string, indentLevel) # add the digit
            tokenizer.nextToken()
        elif(tokenizer.currentToken() != "("):
            self.id = idClass()
            string = self.id.printId(tokenizer, False, string, indentLevel)
        else:
            #Parse the expression
            string = addToString(tokenizer.currentToken(), string, indentLevel) #  (
            tokenizer.nextToken()
            self.expr = expr()
            string = self.expr.printExpr(tokenizer, string, indentLevel)
            string = addToString(tokenizer.currentToken(), string, indentLevel) #  )
            tokenizer.nextToken()

        return string

    def evalFac(self):
        result = "null"
        if(self.alt == 1):
            result = self.int
        elif(self.alt == 2):
            result = getIdValue(self.id)
        elif(self.alt == 3):
            result = self.expr.evalExpr()

        return result

def matchAndConsume(tokenizer, match):
        #If the next token does not patch, print an error
        if (tokenizer.currentToken() != match):
            sys.exit("Error - expected '" + match + "' - Received '" + tokenizer.currentToken() + "' - Line " + tokenizer.getCurrentLine())
        elif tokenizer.currentToken() != "EOF":
            tokenizer.nextToken()

#Add the given value to the string. String is the currect line being printed to the console
def addToString(add, string, indentLevel):

    #If it is a fresh line, apply appropriate indents
    if (string == ""):
        for i in range(indentLevel):
            string += "  "

    if(add == ";" or add == "," ):
        string = string[:-1] #remove the space before these symbols

    string += add + " "

    return string

def printAndClearString(string):
    print(string[:-1]) #print without the additional space on the end
    string = "" #reset the string
    return string

#Retrieves the value of the id from the symbol table,
#internally handles checking if the ID has been initialized
#Parameter should be of type "idClass"
def getIdValue(check):
    curSym = check.getSymbol()
    curVal = symbolTable[curSym]
    if(curVal == "null"):
        sys.exit("ERROR - Attempting to use uninitialized id " + curSym)
    else:
        return curVal



#Program start point. Open file, create tokenizer, parse it, then print it
symbolTable = {}
fileName = sys.argv[1]
inputFile = open(fileName,'r')
tokenizer = Tokenizer(inputFile)
tokenizer.nextToken()

outputString = ""
indentLevel = 0

program = Prog()
program.parseProg(tokenizer)
#program.printProg(tokenizer, outputString, indentLevel)

program.execProg()