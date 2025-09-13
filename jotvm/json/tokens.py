import re


TOKEN_SPECIFICATION = [
    ('NUMBER', r'[+-]?(\d*\.\d+|\d+\.?)([eE][+-]?\d+)?'),
    ('STRING', r'"([^"\\]|\\.)*"'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COLON', r':'),
    ('COMMA', r','),
    ('TRUE', r'true'),
    ('FALSE', r'false'),
    ('NULL', r'null'),
    ('SKIP', r'[ \t\n\r]+'),
    ('MISMATCH', r'.'),
]


TOK_REGEX = '|'.join(
    (f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)
)


def tokenize(json_string: str, tok_regex):
    for mo in re.finditer(tok_regex, json_string):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'MISMATCH':
            raise SyntaxError(
                f'Unexpected value `{value}` encountered'
            )
        if kind != 'SKIP':
            yield kind, value


class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0 

    def peek(self):
        """Peek at the next token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def consume(self, expected=None):
        """Consume the current token and return it."""
        if self.position >= len(self.tokens):
            raise SyntaxError('Unexpected end of input')
        token = self.tokens[self.position]
        if expected and token[0] != expected:
            raise SyntaxError('Expected `{expected}`, but got {token[0]}')
        self.position += 1
        return token

    def has_more(self):
        """Check if there are more tokens."""
        return self.position < len(self.tokens)
