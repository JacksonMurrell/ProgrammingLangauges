import string
import re
import sys

# Yes I copied this in two places, but it's the lazy solution until I can
# get this properly enumed.
ID = 1       # identifier
LPAR = 2     # (
RPAR = 3     # )
NOT = 4      # !
AND = 5      # /\
OR = 6       # \/
IMPLIES = 7  # =>
IFF = 8      # <=>
COMMA = 9    # ,
INTEGER = 10 # 0-9 integers

expressions = ((r'\n',                    None),
               (r' +',                    None),   # Whitespace
               (r'\(',                    LPAR),
               (r'\)',                    RPAR),
               (r'!',                     NOT),
               (r'/\\',                   AND),
               (r'\\/',                   OR),
               (r'=>',                    IMPLIES),
               (r'<=>',                   IFF),
               (r',',                     COMMA),
               (r'[0-1]+',                INTEGER),
               (r'[A-Za-z][A-Za-z0-9_]*', ID),
             )

def tag_to_string(tag):
    if tag == ID:
        return "ID"
    if tag == LPAR:
        return "LPAR"
    if tag == RPAR:
        return "RPAR"
    if tag == NOT:
        return "NOT"
    if tag == AND:
        return "AND"
    if tag == OR:
        return "OR"
    if tag == IMPLIES:
        return "IMPLIES"
    if tag == IFF:
        return "IFF"
    if tag == COMMA:
        return "COMMA"
    if tag == INTEGER:
        return "INTEGER"

class Token:
    # This is to be able to store the location data inside the token.
    def __init__(self, symbol, tag, row, column):
        self.symbol = symbol
        self.tag = tag
        self.row = row
        self.column = column

    def __str__(self):
        return str(self.tag)

class Lexer:
    def __init__(self, text, expressions):
        self.text = text
        self.line = 1
        self.col = 1
        self.expressions = expressions
        self.current_token = None
        self.tokens = []

    def tokenize(self):
        pos = 0
        row = 1
        column = 1
        lexer_error = False
        # This works as a "lookahead" lexer.  We check, at each point, if the characters
        # ahead match any of our expression.  If so, match it and increment one.
        # We are only checking at the start of the string.
        while pos < len(self.text):
            current_match = None
            token = None
            for expr, tag in self.expressions:
                regex = re.compile(expr)
                current_match = regex.match(self.text, pos)
                if current_match:
                    # Get the text of the match.
                    token = current_match.group(0)
                    # If tag is None, then it's a comment, whitespace, or some other such thing.
                    # Don't add it if this is the case.
                    if tag:
                        self.tokens.append(Token(token, tag, row, column))
                    break
            if not current_match:
                import pdb;pdb.set_trace()
                print 'Illegal character \'' + self.text[pos] + '\' at ' + self.text[pos] + " on line " + str(column) + " and column " + str(column)
                pos += 1
                column += 1
                lexer_error = True
                continue
            # If we find something like a variable name, skip ahead that many characters.
            pos += len(token)
            column += 1
        return self.tokens if not lexer_error else -1

def imp_lex(text):
    return Lexer(text, expressions).tokenize()
