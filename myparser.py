from contextlib import suppress
import pyparsing as pp
from pyparsing import pyparsing_common as ppc
from ASTree import *


def make_parser():
    MULT = pp.oneOf('* /')
    ADD = pp.oneOf('+ -')
    COND = pp.oneOf('== != > < >= <=')
    LOGIC = pp.oneOf('&& ||')
    #ASSIGN = pp.oneOf('+= -=')

    RIGHTP, LEFTP, LEFTBR, RIGHTBR, LEFTSQ, RIGHTSQ = pp.Literal(')').suppress(), pp.Literal('(').suppress(),\
                                                      pp.Literal('{').suppress(), pp.Literal('}').suppress(),\
                                                      pp.Literal('['), pp.Literal(']')
    SIGN = pp.oneOf('= += -= *= /=')
    DOUBLEOP = pp.oneOf(' ++ --')
    ENDSTR = pp.Literal(';').suppress()
    COMMA = pp.Literal(',').suppress()
    DOT = pp.Literal('.').suppress()

    BOOLEAN = pp.Keyword('true') #| pp.Keyword('false')
    CLASS = pp.Keyword('class')
    PRINT = pp.Keyword('Console.WriteLine')
    NEW = pp.Keyword('new')
    ACCESS = pp.oneOf('public private')#pp.Keyword('public')
    STATIC = pp.Keyword('static')
    IF, ELSE = pp.Keyword('if'), pp.Keyword('else')
    FOR, WHILE, DO = pp.Keyword('for'), pp.Keyword('while'), pp.Keyword('do')
    RETURN = pp.Keyword('return')

    add = pp.Forward()
    block = pp.Forward()
    ident = pp.Forward()
    var = pp.Forward()
    condelse = pp.Forward()
    class_1 = pp.Forward()
    numb = ppc.number
    str_ = pp.QuotedString('"')
    literal = numb | str_
    bool = BOOLEAN

    ret = RETURN.suppress() + add + ENDSTR
    cons = pp.ZeroOrMore((var | add) + pp.Optional(COMMA))
    call = pp.Optional(NEW) + (PRINT | ident) + LEFTP + pp.ZeroOrMore((var | add) + pp.Optional(COMMA)) + RIGHTP + pp.Optional(ENDSTR)
    group = bool | call | ident | literal | LEFTP + add + RIGHTP
    ident << ppc.identifier + pp.Optional(LEFTSQ + pp.Optional(group) + RIGHTSQ)
    mult = group + pp.ZeroOrMore(MULT + group)
    add << mult + pp.ZeroOrMore(ADD + mult)
    cond = add + COND + add
    cond_list = LEFTP + cond + pp.ZeroOrMore(LOGIC + cond) + RIGHTP

    array = NEW.suppress() + ident + pp.Optional(LEFTSQ + cons + RIGHTSQ) + pp.Optional((LEFTBR + cons + RIGHTBR)) | (
                LEFTBR + cons + RIGHTBR)
    # increment = DOUBLEOP + ident | ident + DOUBLEOP + pp.Optional(ENDSTR)
    sign = (DOUBLEOP + ident | ident + DOUBLEOP | ident + SIGN + (call | array | add)) + pp.Optional(ENDSTR)
    # pp.Optional(SIGN) + ident + SIGN + pp.Optional((array | call | add)) + pp.Optional(ENDSTR)
    var << pp.Optional(ACCESS) + pp.Optional(STATIC) + ident + (sign | ident) + pp.Optional(ENDSTR)

    condif = IF.suppress() + cond_list + pp.Optional(block) + pp.Optional(condelse)
    condelse << ELSE.suppress() + (condif | pp.Optional(block))
    for_circle = FOR.suppress() + LEFTP + pp.Optional(var | sign) + cond + ENDSTR + pp.Optional(
        var | sign) + RIGHTP + block
    while_circle = WHILE.suppress() + LEFTP + cond + RIGHTP + pp.Optional(block)
    do_circle = DO.suppress() + block + WHILE.suppress() + while_circle + ENDSTR
    func = (var | pp.Optional(ACCESS) + ident) + LEFTP + cons + RIGHTP + block
    expression = ret | call | sign | var | condif | for_circle | while_circle | do_circle | func  # |inner
    block << LEFTBR + pp.ZeroOrMore(expression) + RIGHTBR
    class_1 << pp.Optional(ACCESS) + CLASS.suppress() + ident + LEFTBR + pp.ZeroOrMore(func | var | class_1) + RIGHTBR

    expr_lines = pp.ZeroOrMore(class_1)
    program = expr_lines.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.stringEnd
    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement) -> None:
        if rule_name == rule_name.upper():
            return
        if rule_name in ('mult', 'add', 'cond', 'cond_list'):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                for i in range(1, len(tocs) - 1, 2):
                    node = BOperNode(BinOperation(tocs[i]), node, tocs[i + 1])
                return node
            parser.setParseAction(bin_op_parse_action)
        else:
            cls = ''.join(x.capitalize() or '_' for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                parser.setParseAction(lambda s, loc, tocs: cls(*tocs))

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)
    return start


def parse(string) -> ExprLinesNode:
    res = make_parser().parseString(string)[0]
    res.semantic()
    return res