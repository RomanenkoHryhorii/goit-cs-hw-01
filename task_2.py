import operator

# 1. Розширюємо типи токенів (TokenType)
class TokenType:
    INTEGER = 'INTEGER'  # Ціле число
    PLUS = 'PLUS'        # +
    MINUS = 'MINUS'      # -
    MUL = 'MUL'          # * (Множення)
    DIV = 'DIV'          # / (Ділення)
    LPAREN = 'LPAREN'    # ( (Відкриваюча дужка)
    RPAREN = 'RPAREN'    # ) (Закриваюча дужка)
    EOF = 'EOF'          # Кінець файлу (виразу)

# Клас для представлення токена
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """Рядкове представлення об'єкта класу Token."""
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()

# Клас лексера, відповідає за розбиття виразу на токени
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self):
        raise Exception('Некоректний символ')

    def advance(self):
        """Перехід до наступного символу."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Пропуск пробілів."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Повертає багатоцифрове ціле число."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    # Модифікуємо get_next_token для розпізнавання нових символів
    def get_next_token(self):
        """Лексичний аналізатор (сканер)."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')

            # Нові операції та дужки
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            # Кінець нових символів
            
            self.error()

        return Token(TokenType.EOF, None)

# --- АБСТРАКТНЕ СИНТАКСИЧНЕ ДЕРЕВО (AST) ---
class AST:
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

# --- ПАРСЕР ---
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Некоректний синтаксис')

    def eat(self, token_type):
        """Порівнює поточний тип токена з очікуваним і переходить до наступного."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    # Додано метод factor() для обробки найнижчого рівня ієрархії
    def factor(self):
        """factor: INTEGER | LPAREN expr RPAREN"""
        token = self.current_token
        
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
             # Обробка унарного мінуса (опціонально, але корисно)
            if token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                node = BinOp(Num(Token(TokenType.INTEGER, 0)), Token(TokenType.MINUS, '-'), self.factor())
                return node
            
            self.error()

    # Змінено метод term() для обробки MUL та DIV
    def term(self):
        """term: factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    # Змінено метод expr() для обробки PLUS та MINUS, викликаючи term()
    def expr(self):
        """expr: term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node
    
    def parse(self):
        return self.expr()

# --- ІНТЕРПРЕТАТОР ---
class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        """Доповнюємо метод для обробки MUL та DIV."""
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            # Використовуємо цілочисельне ділення (якщо потрібно)
            # Якщо потрібне ділення з плаваючою точкою, використовуйте /
            right_val = self.visit(node.right)
            if right_val == 0:
                 raise ZeroDivisionError("Спроба ділення на нуль.")
            # Використовуємо // для цілочисельного ділення
            return self.visit(node.left) // right_val 

    def visit_Num(self, node):
        return node.value

    def visit(self, node):
        """Універсальний метод для відвідування вузлів AST."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Немає методу visit_{type(node).__name__}')

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

# --- ТЕСТУВАННЯ ---
def main():
    print("--- Арифметичний Інтерпретатор v2.0 ---")
    print("Підтримує: +, -, *, /, ( )")
    print("Для виходу введіть 'exit'.")
    
    while True:
        try:
            text = input('Введіть вираз> ')
            if text.lower() == 'exit':
                break
            
            if not text.strip():
                continue

            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print(f"Результат: {result}")
        
        except (Exception, ZeroDivisionError) as e:
            print(f"Помилка: {e}")
            continue

if __name__ == '__main__':
    main()
