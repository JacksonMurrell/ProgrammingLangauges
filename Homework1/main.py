import unittest
import sys
from lexer import Lexer, imp_lex, tag_to_string
from parser import parse

def exception_handler(exception_type, exception, traceback,
                      debug_hook=sys.excepthook):
    """
        Overrides the default exception handler to allow for post mortem debugging.
    """
    import pdb
    debug_hook(exception_type, exception, traceback)
    pdb.post_mortem(traceback)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        sys.excepthook = exception_handler
    filename = sys.argv[1]
    file = open(filename)
    line_count = 1
    for line in file:
        tokens = imp_lex(line)
        if tokens == -1:
            print "Encountered lexing error, aborting..."
            sys.exit(1)

        print "Lexer Results for Line: " + str(line_count)
        token_list = []
        for token in tokens:
            token_list.append(tag_to_string(token.tag))
            #print "Symbol: " + token.symbol +" Token: "+ str(token.tag) + " Row: " + str(token.row) + " Column: " + str(token.column)
        print token_list
        print "\n Parser Results for Line: " + str(line_count) + ""
        parse(tokens)
        print "\n"
        line_count += 1
    file.close()
