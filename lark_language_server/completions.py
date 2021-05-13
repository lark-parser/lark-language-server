from . import lark_grammar
from typing import List, NamedTuple
from enum import Enum
from lark.visitors import Visitor
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
)


class TokenType(Enum):
    RULE = "RULE"
    TERMINAL = "TERMINAL"


class Local(NamedTuple):
    name: str
    type_of_token: TokenType


class LocalGetterVisitor(Visitor):
    def __init__(self, *args, **kwargs):
        self.locals = []
        super().__init__(*args, **kwargs)

    def rule(self, tree):
        name = tree.children[0]
        if name[0] == "!":
            name = name[1:]
        self.locals.append(name)


def get_locals_for(doc: str) -> List[CompletionItem]:
    try:
        parsed = lark_grammar.lark_grammar_parser.parse(doc)
    except:
        return []
    # try:
    #     return [
    #         definition.children[0]
    #         if not definition.children[0][0] == "!"
    #         else definition[0][1:]
    #         for definition in lark_grammar.lark_grammar_parser.parse(doc).find_pred(
    #             lambda node: node.data in {"rule", "token"}
    #         )
    #     ]
    # except:
    # return []
    local_getter = LocalGetterVisitor()
    local_getter.visit(parsed)
    return [CompletionItem(item) for item in local_getter.locals]
