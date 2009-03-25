import sys

from picoparse import choice, p, one_of, many, many1, tri, eof, not_followed_by, satisfies, string, commit, optional, sep1, desc, not_one_of
from picoparse.text import run_text_parser, whitespace

reserved_words = ["let", "in", "fn", "def"]
reserved_operators = ["=", "->"]
operator_chars = "+-*/!<>=@$%^&~|?"

def identifier_char1():
  return satisfies(lambda l: l.isalpha() or l == "_")

def identifier_char():
  return choice(identifier_char1, digit)

def digit():
  return satisfies(lambda l: l.isdigit())

@tri
def number():
  whitespace()
  lead = u''.join(many1(digit))
  commit()
  if optional(p(one_of, '.')):
    trail = u''.join(many1(digit))
    return ('float', float(lead + '.' + trail))
  else:
    return ('int', int(lead))

def string_char(quote):
  char = not_one_of(quote)
  if char == '\\':
    char = any_token()
  return char

@tri
def string_literal():
  whitespace()
  quote = one_of('\'"')
  commit()
  st = u''.join(many1(p(string_char, quote)))
  one_of(quote)
  return ('str', st)

def value():
  return choice(number, string_literal)



@tri
def reserved(name):
  assert name in reserved_words
  whitespace()
  string(name)
  not_followed_by(identifier_char)
  return name

@tri
def identifier():
  whitespace()
  not_followed_by(p(choice, *[p(reserved, rw) for rw in reserved_words]))
  first = identifier_char1()
  commit()
  rest = many(identifier_char)
  name = u''.join([first] + rest)
  return ('ident', name)



def operator_char():
  return one_of(operator_chars)

@tri
def operator():
  whitespace()
  not_followed_by(p(choice, *[p(reserved_op, op) for op in reserved_operators]))
  name = u''.join(many1(operator_char))
  return ('op', name)

@tri
def reserved_op(name):
  assert name in reserved_operators
  whitespace()
  string(name)
  not_followed_by(operator_char)
  return name

@tri
def special(name):
  whitespace()
  string(name)
  return name

def expression():
  return choice(eval_expression, let_expression, fn_expression)

def eval_expression():
  parts = many1(expression_part)
  where <- optional(where_expression, None)
  if len(parts) == 1:
    return parts[0]
  else:
    return ('eval', parts, where)

def expression_part():
  return choice(value, identifier, operator, parenthetical)

def binding():
  name = identifier()
  reserved_op('=')
  expr = expression()
  return ('bind', name, expr)

def let_expression():
  reserved('let')
  bindings = sep1(let_binding, p(special, ','))
  reserved('in')
  expr = expression()
  return ('let', bindings, expr)

def where_expression():
  reserved('where')
  return sep1(let_binding, p(special, ','))

def fn_expression():
  reserved('fn')
  params = many1(identifier)
  reserved_op('->')
  expr = expression()
  return ('fn', params, expr)

def parenthetical():
  special("(")
  expr = expression()
  special(")")
  return expr

def definition():
  reserved('def')
  name = identifier()
  reserved_op('=')
  expr = expression()
  return ('def', name, expr)

def semi():
  return special(';')

def program_part():
  expr = choice(definition, expression)
  optional(semi)
  return expr

def program():
  prog = many(program_part)
  whitespace()
  eof()
  return ('prog', prog)

if __name__ == "__main__":
    text = """
    def fib = fn n ->
        if (n == 0)
            then 0
            else (fib (n - 1) + fib (n - 2));
    let x = 5, y = 4
    in fib (x * y)
    """
    if len(sys.argv) > 1:
        text = sys.argv[1]
    print run_text_parser(program, text)

