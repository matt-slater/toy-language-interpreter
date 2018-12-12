import re
ID, LITERAL, DIGIT, LETTER, PLUS, MINUS, MULT, SEMICOLON, LPAREN, RPAREN, EQUAL, EOF = \
    'ID', 'LITERAL', 'DIGIT', 'LETTER','PLUS', 'MINUS', 'MULT', 'SEMICOLON', 'LPAREN', 'RPAREN', 'EQUAL', 'EOF'

class AST(object):
    pass

class NoOp(AST):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Identifier(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    def __init__(self):
        self.children = []

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type = self.type,
            value = repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid Character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def digit(self):
        result = ''
        result += self.current_char
        self.advance()
        return result

    def isLetter(char, z):
        # return re.match(r'[a-zA-Z_]', z)
        if re.match(r'[a-zA-Z_]', z):
            return True
        else:
            return False

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(DIGIT, self.digit())

            if self.current_char == '*':
                self.advance()
                return Token(MULT, '*')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == ';':
                self.advance()
                return Token(SEMICOLON, ';')

            if self. current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '=':
                self.advance()
                return Token(EQUAL, '=')

            if self.isLetter(self.current_char):
                result = self.current_char
                self.advance()
                return Token(LETTER, result)

            self.error()

        return Token(EOF, None)


class Parser(object):
    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid Syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def digit(self):
        ## Digit --> 0 | 1 | ... | 9
        token = self.current_token
        self.eat(DIGIT)
        return Num(token)

    def nonzerodigit(self):
        ## NonZeroDigit --> 1 | ... | 9
        token = self.current_token
        if token.value != '0':
            self.eat(DIGIT)
            return Num(token)

    def letter(self):
        ## Letter --> a | ... | z | A | ... | Z | _
        token = self.current_token
        self.eat(LETTER)
        return token.value

    def identifier(self):
        ## Identifier --> Letter [ Letter | Digit ]*
        result = self.letter()

        while self.current_token.type in (LETTER, DIGIT):
            token = self.current_token
            if token.type == LETTER:
                addon = token.value
                self.eat(LETTER)
                result += addon
            elif token.type == DIGIT:
                addon = token.value
                self.eat(DIGIT)
                result += addon

        return Identifier(Token(ID, result))

    def assignment(self):
        ## Assignment --> Identifier =  Exp ;
        left = self.identifier()
        token = self.current_token
        self.eat(EQUAL)
        right = self.exp()
        node = Assign(left, token, right)
        self.eat(SEMICOLON)
        return node

    def fact(self):
        ## Fact --> ( Exp ) | - Fact | + Fact | Literal | Identifier
        token = self.current_token
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.exp()
            self.eat(RPAREN)
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.fact())
            return node
        elif token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.fact())
            return node
        elif token.type == DIGIT:
            return self.literal()
        elif token.type == LETTER:
            node = self.identifier()
            return node

    def program(self):
        ## Program --> Assignment*
        root = Compound()
        token = self.current_token
        while token.type is not EOF:
            root.children.append(self.assignment())
            token = self.current_token
        return root

    def term(self):
        ## Term --> Fact Term'
        result = self.fact()
        node = self.termprime()
        if node is NoOp:
            return result
        else:
            return BinOp(result, node.token, node)

    def termprime(self):
        ## Term' --> * Fact Term' | e
        token = self.current_token
        if token.type == MULT:
            self.eat(MULT)
            result = self.fact()
            node = self.termprime()
            if node is NoOp:
                return BinOp(result, token, Num(Token(LITERAL, 1)))
        return NoOp

    def exp(self):
        ## Exp --> Term Exp'
        result = self.term()
        node = self.expprime()
        if node is NoOp:
            return result
        else:
            return BinOp(result, node.token, node)

    def expprime(self):
        ## Exp' --> + Term Exp' | - Term Exp' | e
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            left = self.term()
            right = self.expprime()
            if right is NoOp:
                return BinOp(left, token, Num(Token(LITERAL, 0)))

        elif token.type == MINUS:
            self.eat(MINUS)
            left = self.term()
            right = self.expprime()
            if right is NoOp:
                return BinOp(left, token, Num(Token(LITERAL, 0)))
        return NoOp

    def literal(self):
        ## Literal -->  0 | NonZeroDigit Digit*
        token = self.current_token

        if token.type == DIGIT and token.value == '0':
            self.eat(DIGIT)
            return Num(Token(LITERAL, 0))
        elif token.type ==DIGIT and token.value is not '0':
            result = token.value
            self.eat(DIGIT)
            token = self.current_token
            while token.type == DIGIT:
                result += token.value
                self.eat(DIGIT)
                token = self.current_token

            return Num(Token(LITERAL, int(result)))

class NodeVisitor(object):
    def visit(self, node):
        methodname = 'visit_' + type(node).__name__
        visitor = getattr(self, methodname, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(node.value)
        raise Exception('No visit_{} method'.format(type(node).__name__) + ' ' + node.type)

class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):

        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MULT:
            return self.visit(node.left) * self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Identifier(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

def main():
    while True:
        try:
            text = raw_input('toy-lang> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()
        print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
    main()
