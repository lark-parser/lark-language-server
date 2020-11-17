from contextlib import suppress
from typing import List, Union
import logging
from lark import UnexpectedToken, Token, Lark, UnexpectedCharacters
from lark.lexer import Lexer, TraditionalLexer
from lark.common import LexerConf
from pygls.types import (Diagnostic, Range, Position)

from .lark_grammar import lark_grammer


def user_repr(error: Union[UnexpectedToken]):
    if isinstance(error, UnexpectedToken):
        expected = ', '.join(error.accepts or error.expected)
        return f"Unexpected token {str(error.token)!r}. Expected one of:\n{{{expected}}}"
    else:
        return str(error)


class CustomLexerState:
    __slots__ = 'tokens', 'index'

    def __init__(self, tokens, index=0):
        self.tokens = tokens
        self.index = index

    def __copy__(self):
        return type(self)(self.tokens, self.index)


class CustomLexer(Lexer):
    def __init__(self, conf: LexerConf):
        self.lexer = TraditionalLexer(conf)

    def make_lexer_state(self, text: str):
        lexer_state = self.lexer.make_lexer_state(text)
        tokens = []
        while True:
            try:
                tokens.append(self.lexer.next_token(lexer_state))
            except EOFError:
                break
            except UnexpectedCharacters as e:
                lexer_state.line_ctr.feed(e.char)
                # With `<>` it can not be normally generated from a grammar. And the special value used inside of Lark is `<EOF>`
                tokens.append(Token('<ERROR>', e, line=e.line, column=e.column,
                                    end_line=lexer_state.line_ctr.line, end_column=lexer_state.line_ctr.column,
                                    pos_in_stream=e.pos_in_stream, end_pos=lexer_state.line_ctr.char_pos))
        return CustomLexerState(tokens)

    def next_token(self, state: CustomLexerState):
        if state.index >= len(state.tokens):
            raise EOFError
        state.index += 1
        return state.tokens[state.index - 1]

    def lex(self, state: CustomLexerState, parser_state):
        with suppress(EOFError):
            while True:
                yield self.next_token(state)

    def scroll_to(self, state: CustomLexerState, token_type: str):
        """ Scrolls through the token list till we find a Token with type token_type"""
        while state.index < len(state.tokens):
            if state.tokens[state.index].type == token_type:
                break
            else:
                state.index += 1
    
    __future_interface__ = True

lark_debug_parser = Lark(lark_grammer, parser='lalr', debug=True, lexer=CustomLexer)


states = lark_debug_parser.parser.parser.parser.parse_table.states

target_rules = {'_item'}

target_states = set()

for s in states:
    for r in s:
        if r.rule.origin.name in target_rules and r.index == 0:
            target_states.add(s)
            break

def get_diagnostics(doctext: str):
    diagnostics: List[Diagnostic] = []

    def on_error(e: UnexpectedToken):
        t = e.token
        diagnostics.append(Diagnostic(
            Range(
                Position(t.line - 1, t.column - 1),
                Position(t.end_line - 1, t.end_column - 1)
            ),
            user_repr(e)))
        p = e.puppet
        ps = p.parser_state
        ls = p.lexer_state
        ls.lexer.scroll_to(ls.state, '_NL')
        ls.lexer.next_token(ls.state)
        while ps.state_stack[-1] not in target_states:
            ps.state_stack.pop()
            ps.value_stack.pop()
        return True

    try:
        lark_debug_parser.parse(doctext, on_error=on_error)
    except Exception as e:
        logging.exception(f"parser raised exception: {type(e)}")
    return diagnostics
