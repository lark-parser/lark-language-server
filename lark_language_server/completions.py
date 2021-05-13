from . import lark_grammar
from typing import List, NamedTuple
from enum import Enum
from lark.visitors import Visitor
class TokenType(Enum):
    RULE = "RULE"
    TERMINAL = "TERMINAL"

class Local(NamedTuple):
    name: str
    type_of_token: TokenType

        
class LocalGetterVisitor(Visitor):
    def __init__(self):
        self.locals = []
        super().__init__()
    def rule(self, tree):
        name = tree.children[0]
        if name[0] == "!": name = name[1:]
        self.locals.append(name)
    
def get_locals_for(doc: str) -> List[str]:
    parsed = lark_grammar.lark_grammar_parser.parse(doc)
    local_getter = LocalGetterVisitor.visit(parsed)
    return local_getter.locals
    
