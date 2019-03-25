import sys
from lexer import lex, tag_to_string
from parser import parse
from pysmt.shortcuts import Symbol, Not, Or, And, Implies, Iff, is_sat
# P is True Q is False
input_lines = ["!(P /\ !Q)", "P /\ !P"]

dict_enum = {1: "ID",
             2: "LPAR",
             3: "RPAR",
             4: "NOT",
             5: "AND",
             6: "OR",
             7: "IMPLIES",
             8: "IFF",
             10: "INTEGER"}

OPERANDS = ["AND", "OR", "NOT", "IMPLIES", "IFF", "LPAR", "RPAR"]

# From first to last in order of operations.
precedence = {"LPAR":    4,
              "NOT":     3,
              "AND":     2,
              "OR":      2,
              "IMPLIES": 1,
              "IFF":     1}

op_map = {"NOT": Not,
              "AND": And,
              "OR": Or,
              "IMPLIES": Implies,
              "IFF": Iff,}


def exception_handler(exception_type, exception, traceback,
                      debug_hook=sys.excepthook):
    """
        Overrides the default exception handler to allow for post mortem debugging.
    """
    import pdb
    debug_hook(exception_type, exception, traceback)
    pdb.post_mortem(traceback)

def strip_leaves(parse_tree):
    variables = []
    operands = []
    for item in parse_tree:
        if type(item) is tuple:
            # TODO: Allow multiple types of variables
            symbol = Symbol(item[1])
            variables.append(Symbol(item[1]) if item[1] == "P" else Not(Symbol(item[1])))
        if item in OPERANDS:
            operands.append(item)
    return (variables, operands)

def main():
    if "--debug" in sys.argv or "-d" in sys.argv:
        sys.excepthook = exception_handler

    raw_file = open(sys.argv[1])
    line_count = 1

    # Add a bit of readibility buffer between the output and the terminal prompt.
    print ""
    for line in raw_file:
        tokens = lex(line, line_count)
        if tokens == -1:
            print "Lexing failed, please remove illegal characters."
            print ""
            return -1

        # If this fails to parse due to a syntax error, it will output the column in which it failed
        # instead.  The parse prints out the error, row, and column number.
        parse_tree = parse(tokens)
        if type(parse_tree) is int:
            print ""
            continue

        variable_stack, operator_list = strip_leaves(parse_tree)
        operator_list.reverse()

        # Handle the unary versus binary operators.
        get_vars = lambda op, var_list: [var_list.pop()] if op == "NOT" else [var_list.pop(), var_list.pop()]

        operator_stack = [operator_list.pop()]

        # This algorithim is basically a modified "Shunting Yard" algorithim.
        while operator_list:
            # The operator popped from our master operator list.
            op_list_var = operator_list.pop()
            # We still need to handle precendence order within the parenthesis,
            # so we will "start over" in essence with a new stack, and then add the
            # result back to our main variable stack.
            if op_list_var == "LPAR":
                # The operator popped from our stack.
                op = operator_list.pop()
                parenthesis_stack = []
                while op != "RPAR":
                    parenthesis_stack.append(op)
                    # If what is on the top of the stack has higher precedence than our current op,
                    # deal with what's on the stack first.
                    while operator_stack and precedence.get(parenthesis_stack[-1], 0) > precedence.get(op, 0):
                        variables = get_vars(op, variable_stack)
                        variable_stack.append(op_map[op](*variables))
                    op = operator_list.pop()

                # Since everything here has higher precedence, go ahead and resolved all operators.
                while parenthesis_stack:
                    op = parenthesis_stack.pop()
                    op_vars = get_vars(op, variable_stack)
                    variable_stack.append(op_map[op](*op_vars))

            else:
                variables = get_vars(op_list_var, variable_stack)
                # If what is on the top of the stack has higher precedence than our current op,
                # deal with what's on the stack first.
                while operator_stack and precedence.get(operator_stack[-1], 0) > precedence.get(op_list_var, 0):
                    # The operator popped from our stack.
                    op = operator_stack.pop()
                    # If we need to pop, pop from the already in-use variables.
                    # There may be nothing left on the variable stack.
                    op_vars = get_vars(op, variables)
                    variable_stack.append(op_map[op](*variables))

                operator_stack.append(op_list_var)
                variable_stack.extend(variables)

        while operator_stack:
            op = operator_stack.pop()
            op_vars = get_vars(op, variable_stack)
            variable_stack.append(op_map[op](*op_vars))

        # Clear temp variables for the next round if needed.
        op_list_var = None
        op = None

        print "Line " + str(line_count) + " Statement: " + line
        print "Is Satisfiable? " + str(is_sat(variable_stack.pop()))
        print ""

        line_count += 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
