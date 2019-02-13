import unittest
import sys
from lexer import Lexer, imp_lex
from parser import parse

if __name__ == '__main__':
    filename = sys.argv[1]
    file = open(filename)
    characters = file.read()
    file.close()
    tokens = imp_lex(characters)
    if tokens == -1:
    	print "Encountered lexing error, aborting..."
    	sys.exit(1)

    print "Lexer Results:"
    for token in tokens:
        #import pdb;pdb.set_trace()
        print "Symbol: " + token.symbol +" Token: "+ str(token.tag) + " Row: " + str(token.row) + " Column: " + str(token.column)
    
    print "\n Parser Results:"
    parse(tokens)