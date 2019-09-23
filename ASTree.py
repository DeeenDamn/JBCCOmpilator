from abc import ABC, abstractmethod
from typing import Tuple
from enum import Enum
import random
import string


class ASTreeNode(ABC):
    @property
    def child(self)->Tuple['ASTreeNode', ...]:
        return ()

    @abstractmethod
    def __str__(self)->str:
        pass

    def semantic(self, context: 'Context' = None):
        stack = 0
        for each in self.child:
            stack += each.semantic(context)
        return stack

    def compile(self, file=None):
        for each in self.child:
            each.compile(file)

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        children = self.child
        symb1 = '|~'
        for i in range(len(children)):
            symb2 = '| '
            if i == len(children) - 1:
                symb2 = '  '
            res.extend((symb1 if j == 0 else symb2) + ' ' + children[i].tree[j] for j in range(len(children[i].tree)))
        return res

class VarType(Enum):
    Global = 'global'
    Local = 'local'
    Param = 'param'


class Context(object):
    def __init__(self, parent: 'Context' = None):
        self.name = []
        self.vars = []
        self.params = []
        self.parent = parent
        self.label = 0

    def find_func(self, name, params):
        local_context = self
        while local_context:
            for func in local_context.vars:
                try:
                    if func.params is not None:
                        if str(func.value.value) == str(name.value) and len(func.params.child) == len(params):
                            return func
                except BaseException:
                    pass
            local_context = local_context.parent
        return None

    def get_index(self):
        return len(self.vars)
        '''if len(self.params) > 0 or self.parent == None:
            return len(self.vars)
        else:
            return len(self.vars)+1'''

    def param_in(self, name):
        for x in self.vars:
            if x.value == name:
                return True
        return False

    def add_var(self, var):
        if self.parent == None:
            var.var_type = VarType.Global
        else:
            var.var_type = VarType.Local
        self.vars.append(var)

    def add_par(self, var):
        var.var_type = VarType.Param
        self.params.append(var)

    def add_label(self):
        self.label += 1
        local_context = self
        while local_context.parent:
            tmp = local_context.parent.label - local_context.label
            if tmp < 0:
                local_context.parent.label = local_context.label
            else:
                local_context.label = local_context.parent.label
                local_context.label += 1
                local_context.parent.label += 1
            local_context = local_context.parent
        return self.label


    def find_var_local(self, name):
        try:
            name = name.split('[')[0]
        except Exception:
            pass
        for par in self.vars:
            try:
                var = par.value.split('[')[0]
            except Exception:
                var = par.value
            if name == var:
                return par
        return None

    def get_name(self):
        local_context = self
        while local_context:
            if len(local_context.name) != 0:
                return local_context.name[len(local_context.name)-1]
            local_context = local_context.parent
        return None

    def find_var(self, name):
        local_context = self
        try:
            name = name.split('[')[0]
        except Exception:
            pass
        while local_context:
            for par in local_context.vars:
                try:
                    var = par.value.split('[')[0]
                except Exception:
                    var = par.value
                if name == var:
                    return par
            local_context = local_context.parent
        return None


class ValueNode(ASTreeNode):
    pass


class LiteralNode(ValueNode):
    def __init__(self, numb):
        super().__init__()
        self.type = None
        self.value = numb
        if str(type(self.value))[8:-2] == 'float':
            self.type = 'double'
        elif str(type(self.value))[8:-2] == 'str':
            self.type = 'string'
        else:
            self.type = 'int'

    def semantic(self, context: Context = None):
        return 1

    def compile(self, file=None):
        if self.type == 'int':
            if self.value < 6:
                file.write('{}const_{}\n'.format(str(self.type)[0], self.value))
            else:
                file.write('b{}push {}\n'.format(str(self.type)[0], self.value))
        elif self.type == 'double':
            file.write('ldc2_w {}\n'.format(self.value))
        else:
            file.write('ldc "{}"\n'.format(self.value))

    def strparam(self):
        return self.value

    def __str__(self)->str:
        return str(self.value) + ' (dtype = {})'.format(self.type)


class BoolNode(ValueNode):
    def __init__(self, value: str):
        super().__init__()
        self.type = 'boolean'
        self.value = value

    def semantic(self, context: Context = None):
        return 1

    def compile(self, file=None):
        file.write('iconst_{}\n'.format('1' if self.value == 'true' else '0'))

    def strparam(self):
        return self.value

    def __str__(self)->str:
        return str(self.value) + ' (dtype = {})'.format(self.type)


class Type(ValueNode):
    def __init__(self, type: str):
        self.type = None
        if self.is_type(type):
            self.type = type

    @staticmethod
    def is_type(type):
        if type == 'int':
            return True
        elif type == 'string':
            return True
        elif type == 'boolean':
            return True
        elif type == 'float':
            return True
        elif type == 'double':
            return True
        elif type == 'void':
            return True
        else:
            return False

    def __str__(self):
        return str(self.type)


class Value(ValueNode):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return str(self.name)


class IdentNode(ValueNode):
    def __init__(self, symb: str, *br: Tuple[str]):
        super().__init__()
        self.index = None
        self.var_type = None
        self.type = None
        self.value = None
        self.arr = None
        self.args = None
        self.field = False
        self.static = False
        self.name = None #название класса для вызова полей класса
        if Type.is_type(symb):
            if len(br) > 0:
                if len(br) > 2:
                    self.arr = br[1]
                    self.type = symb + '[{}]'.format(br[1].value if br[1].value is not None else br[1])
                else:
                    self.type = symb + '[]'
            else:
                self.type = symb
        else:
            if len(br) > 2:
                self.arr = br[1]
                self.value = symb + '[{}]'.format(br[1].value if br[1].value is not None else br[1])
            else:
                self.value = symb

    def semantic(self, context: Context = None):
        stack = 0
        if self.arr:
            stack = self.arr.semantic(context)
        if self.value is not None:
            var = context.find_var_local(self.value)
            if var is None:
                var = context.find_var(self.value)
                if var is None:
                    context.add_var(self)
                    self.index = context.get_index()
                else:
                    if var.value == self.value:
                        self.index = var.index
                        self.type = var.type
                        self.var_type = var.var_type
                        self.field = var.field
                        self.static = var.static
                    else:
                        self.index = var.index
                        self.type = var.type.split('[')[0]
            else:
                if var.value == self.value:
                    self.index = var.index
                    self.type = var.type
                    self.var_type = var.var_type
                    self.field = var.field
                    self.static = var.static
                else:
                    self.index = var.index
                    self.type = var.type.split('[')[0]
                if var.var_type is None or var.var_type is VarType.Param:
                    self.var_type = str(VarType.Local)
                else:
                    self.var_type = str(var.var_type)
        if self.field:
            self.name = context.get_name()
        return stack

    def compile(self, file=None):
        if self.field:
            file.write('aload_0\n')
            file.write('get{} {}/{} {}\n'.format('static' if self.static else 'field', self.name, self.value,
                                                 str(self.type)[0].upper()))
        else:
            if self.arr:
                file.write('aload_{}\n'.format(self.index-1))
                self.arr.compile(file)
                file.write('{}aload\n'.format(str(self.arr.type)[0]))
            else:
                file.write('{}load_{}\n'.format(str(self.type)[0] if self.type != 'string' else 'a', self.index-1))

    def strparam(self):
        return '{} {}'.format(str(self.type), str(self.value))

    def __str__(self) -> str:
        if self.value:
            res = '{}'.format(str(self.value))
        else:
            res = '{}'.format(str(self.type))
        if self.args is not None:
            if self.args != '':
                params = ''
                types = ''
                for it in self.args:
                    a = str(type(it))
                    if it != self.args[len(self.args)-1]:
                        params += '{} {}, '.format(it.type, it.value)
                    elif str(type(it)) == '<class \'ASTree.IdentNode\'>' or str(type(it)) == '<class \'ASTree.LiteralNode\'>':
                        params += '{}'.format(it.value)
                        if str(type(it)) != '<class \'ASTree.LiteralNode\'>':
                            types += ' (dtype = {}, vtype = {}, index = {})'.format(it.type, it.var_type,
                                                                                  it.index)
                        else:
                            types += ' (dtype = {}, const = {})'.format(it.type, it.value)
                    elif str(type(it)) == '<class \'ASTree.BOperNode\'>':
                        params += '{}{}{}'.format(it.arg1.value, it.op.value, it.arg2.value)
                        types += ' (dtype = {})'.format(it.type)
                res += '({}){}'.format(params, types)
            else:
                res += '()'
        if self.var_type:
            res += ' (dtype = {}, vtype = {}, index = {})'.format(self.type, self.var_type, self.index)
            if self.arr:
                if str(type(self.arr)) != '<class \'ASTree.LiteralNode\'>':
                    res += ' (dtype = {}, vtype = {}, index = {})'.format(self.arr.type, self.arr.var_type, self.arr.index)
                else:
                    res += ' (dtype = {}, const = {})'.format(self.arr.type, self.arr.value)
        return res


class VarNode(ValueNode):
    def __init__(self, *expr: Tuple[ASTreeNode]):#access: IdentNode, static: IdentNode, value: IdentNode, expr: ASTreeNode):
        self.name = None
        self.type = None
        self.value = None
        self.expr = None
        self.access = None
        self.static = False
        self.field = False
        if len(expr) == 4:
            self.access = expr[0]
            self.static = True
            self.type = expr[2].type
            self.expr = expr[3]
            self.field = True
        elif len(expr) == 3:
            if expr[0] == 'static':
                self.static = True
            else:
                self.access = expr[0]
            self.type = expr[1].type
            self.expr = expr[2]
            self.field = True
        else:
            self.type = expr[0].type if expr[0].type else expr[0].value
            self.expr = expr[1]
        if len(self.expr.child) > 0:
            self.value = self.expr.symb1
        else:
            self.value = self.expr
        self.value.type = self.type
        self.value.field = self.field
        #self.value.access = self.access
        self.value.static = self.static


    def strparam(self):
        return str(self.type) + ' ' + str(self.value)

    def semantic(self, context: Context = None):
        if self.field == False:
            self.field = True if context.parent == None else False
            self.value.field = self.field
        context.add_var(self.value)
        self.value.index = context.get_index()
        #stack = self.value.semantic(context)
        stack = self.expr.semantic(context)
        return stack

    def compile(self, file = None):
        if self.value == self.expr and self.field:
            file.write('.field {} {} {} {}\n'.format(self.access if self.access else '', 'static' if self.static else '',
                                                   self.value.value, str(self.value.type)[0].upper()))
        else:
            self.expr.compile(file)

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr,

    def __str__(self):
        if type:
            return 'var (dtype = {})'.format(self.type)
        return 'var'


class BinOperation(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    EQ = '=='
    NOTEQ = '!='
    BIG = '>'
    SMALL = '<'
    BIG1 = '>='
    SMALL1 = '<='
    AND = '&&'
    OR = '||'


class BOperNode(ValueNode):
    def __init__(self, op: BinOperation, a: ASTreeNode, b: ASTreeNode):
        super().__init__()
        self.op = op
        self.arg1 = a
        self.arg2 = b
        self.const = None
        if str(type(self.arg1)) == '<class \'ASTree.LiteralNode\'>':
            self.const = self.arg1.value
        if str(type(self.arg2)) == '<class \'ASTree.LiteralNode\'>':
            self.const = self.arg2.value
        self.type = None
        self.label = None
        self.rever = False
        self.increment = False

    def dolabel(self, rever = None):
        self.rever = rever
        #if self.label is None:
        #    self.label = 'LABEL0x2'#придумать что-нибудь
        return self.label

    def reverse(self):
        if self.op is BinOperation.EQ:
            return 'ne'
        if self.op is BinOperation.NOTEQ:
            return 'eq'
        if self.op is BinOperation.BIG:
            return 'le'
        if self.op is BinOperation.SMALL1:
            return 'gt'
        if self.op is BinOperation.SMALL:
            return 'ge'
        if self.op is BinOperation.BIG1:
            return 'lt'

    def comp_op(self):
        if self.op is BinOperation.EQ:
            return 'eq'
        if self.op is BinOperation.NOTEQ:
            return 'ne'
        if self.op is BinOperation.BIG:
            return 'gt'
        if self.op is BinOperation.SMALL1:
            return 'le'
        if self.op is BinOperation.SMALL:
            return 'lt'
        if self.op is BinOperation.BIG1:
            return 'ge'
        if self.op is BinOperation.ADD:
            return 'add'
        if self.op is BinOperation.MUL:
            return 'mul'
        if self.op is BinOperation.SUB:
            return 'sub'
        if self.op is BinOperation.DIV:
            return 'div'

    def semantic(self, context: Context = None):
        stack = self.arg1.semantic(context)
        stack += self.arg2.semantic(context)
        if self.op == BinOperation.ADD or self.op == BinOperation.MUL or self.op == BinOperation.DIV or self.op == BinOperation.SUB:
            if str(self.arg1.type) == str(self.arg2.type):
                self.type = self.arg1.type
        else:
            self.type = 'boolean'
            self.label = 'LABEL0x{}'.format(context.add_label())
        return stack - 1 if self.increment else stack

    def compile(self, file=None):
        if self.op == BinOperation.ADD or self.op == BinOperation.MUL or self.op == BinOperation.DIV or self.op == BinOperation.SUB:
            if self.increment:
                file.write('{}{} {} {}\n'.format(str(self.type)[0], 'inc', self.arg1.index, 1 if self.op == BinOperation.ADD else -1))
            else:
                self.arg1.compile(file)
                self.arg2.compile(file)
                file.write('{}{}\n'.format(str(self.type)[0], self.comp_op()))
        else:
            if str(type(self.arg1)) == '<class \'ASTree.LiteralNode\'>':
                if self.arg1.value != 0:
                    self.arg1.compile(file)
            else:
                self.arg1.compile(file)
            if str(type(self.arg2)) == '<class \'ASTree.LiteralNode\'>':
                if self.arg2.value != 0:
                    self.arg2.compile(file)
            else:
                self.arg2.compile(file)
            if self.const is not None and self.const == 0:
                command = ''
            else:
                command = '_{}cmp'.format(str(self.arg1.type)[0])
            if self.rever:
                file.write('if{}{} {}\n'.format(command, self.reverse(), self.label))
            else:
                file.write('if{}{} {}\n'.format(command, self.comp_op(), self.label))

    @property
    def child(self) -> Tuple[ValueNode, ValueNode]:
        return self.arg1, self.arg2

    def strparam(self):
        return str(self.arg1) + ' ' + str(self.op.value) + ' ' + str(self.arg2)

    def __str__(self)->str:
        if type:
            return str(self.op.value) + ' (dtype = {})'.format(self.type)
        return str(self.op.value)


class SignNode(ValueNode):
    def __init__(self, symb1: ASTreeNode = None, sign: str = None, symb2: ASTreeNode=None):
        super().__init__()
        self.post = True if sign else False
        self.sign = sign #if sign else sign1
        self.symb1 = symb1
        if self.sign == '=':
            self.symb2 = symb2
        elif self.sign[1] == '=':
            self.symb2 = BOperNode(BinOperation(str(sign)[0]), self.symb1, symb2)
        else:
            self.symb2 = BOperNode(BinOperation(str(sign)[0]), self.symb1, LiteralNode(1))
            self.symb2.increment = True
        self.type = None
        self.const = None

    def semantic(self, context: Context = None):
        stack = self.symb1.semantic(context)
        stack += self.symb2.semantic(context)
        if str(type(self.symb2)) == '<class \'ASTree.LiteralNode\'>':
            self.const = self.symb2.value
        elif str(type(self.symb2)) == '<class \'ASTree.ArrayNode\'>':
            self.const = self.symb2.const
        if self.symb1.type is not None and self.symb2.type is not None:
            if str(self.symb1.type.split('[')[0]) == str(self.symb2.type.split('[')[0]):
                self.type = self.symb1.type
        return stack

    def compile(self, file=None):
        if self.symb1.field:
            file.write('aload_0\n')
        self.symb2.compile(file)
        if self.symb1.field:
            file.write(
                'put{} {}/{} {}\n'.format('static' if self.symb1.static else 'field', self.symb1.name, self.symb1.value,
                                        str(self.type)[0].upper()))
        #elif str(type(self.symb2)) == '<class \'ASTree.CallNode\'>':
         #   file.write('astore {}\n'.format(self.symb1.index-1))
            #file.write('astore {}\naload {}\npop\n'.format(self.symb1.index, self.symb1.index))
        elif self.type == 'boolean':
            file.write('istore {}\n'.format(self.symb1.index-1))
        elif self.sign == '=' or self.sign[1] == '=':
            file.write('{}store_{}\n'.format(str(self.type)[0] if self.type != 'string' else 'a', self.symb1.index-1))

    @property
    def child(self) -> Tuple[ASTreeNode, ASTreeNode]:
        return self.symb1, self.symb2

    def __str__(self)->str:
        if self.type:
            if self.const is None:
                return '= (dtype = {})'.format(self.type)
            else:
                return '= (dtype = {}, const = {})'.format(self.type, self.const)
        return '='



class RetNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr
        self.type = None

    def semantic(self, context: 'Context' = None):
        stack = 0
        for it in self.child:
            stack += it.semantic(context)
            self.type = it.type
        return stack

    def compile(self, file=None):
        self.expr[0].compile(file)
        file.write('{}return\n'.format(str(self.type)[0]))

    @property
    def child(self)->Tuple[ASTreeNode]:
        return self.expr

    def __str__(self):
        if self.type:
            return 'return (dtype = {})'.format(self.type)
        return 'return'


class CondifNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr
        self.label = None

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr

    def compile(self, file=None):
        labelelse = self.expr[0].dolabel(True)
        self.expr[0].compile(file)
        if str(type(self.expr[len(self.expr)-1])) == '<class \'ASTree.CondelseNode\'>':
            labelend = 'LABEL0x{}'.format(random.choice(string.ascii_lowercase))
            for i in range(1, len(self.expr)-1):
                self.expr[i].compile(file)
            file.write('goto {}\n'.format(labelend))
            file.write('{}:\n'.format(labelelse))
            self.expr[len(self.expr) - 1].compile(file)
            file.write('{}:\n'.format(labelend))
        else:
            for i in range(1, len(self.expr)):
                self.expr[i].compile(file)
            file.write('{}:\n'.format(labelelse))

    def __str__(self) -> str:
        return 'if'


class CondelseNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr

    def compile(self, file=None):
        for i in range(len(self.expr)):
            self.expr[i].compile(file)

    def __str__(self) -> str:
        return 'else'


class ForCircleNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr

    def compile(self, file=None):
        self.expr[0].compile(file)
        label = 'LABEL0x{}'.format(random.choice(string.ascii_lowercase))
        labelend = self.expr[1].dolabel(True)
        file.write(label + ':\n')
        self.expr[1].compile(file)
        for i in range(3, len(self.expr)):
            self.expr[i].compile(file)
        self.expr[2].compile(file)
        file.write('goto {}\n'.format(label))
        file.write('{}:\n'.format(labelend))

    def __str__(self):
        return 'for'


class WhileCircleNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr

    def compile(self, file=None):
        command = str()
        if len(self.expr) > 1:
            labelend = self.expr[0].dolabel(True)
            label = 'LABEL0x{}'.format(random.choice(string.ascii_lowercase))
            file.write(label + ':\n')
            for it in self.expr:
                it.compile(file)
            file.write('goto {}\n'.format(label))
            file.write('{}:\n'.format(labelend))
        else:
            pass#do-while

    def __str__(self):
        return 'while'


class DoCircleNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        self.expr = expr

    @property
    def child(self) -> Tuple[ASTreeNode]:
        return self.expr

    def compile(self, file=None):
        label = self.expr[len(self.expr)-1].expr[0].dolabel()
        file.write(label + ':\n')
        for it in self.expr:
            it.compile(file)


    def __str__(self):
        return 'do'


class ArrayNode(ASTreeNode):
    def __init__(self, *value):
        self.numb = []
        self.const = None
        self.type = None
        for val in value:
            if len(val.child) > 0:
                for it in val.child:
                    if it.type:
                        if self.type is None :
                            self.type = it.type + '[]'
                        elif self.type != it.type + '[]':
                            self.type = 'error'
                    self.numb.append(it)#self.numb.append(it.value if it.value is not None else it)
            else:
                self.type = val.type
                if val.arr:
                    self.const = val.arr.value
        if self.const is None:
            self.const = len(self.numb)

    def semantic(self, context: 'Context' = None):
        if len(self.numb) > 0:
            for it in self.numb:
                it.semantic(context)

        return len(self.numb)*2 + 1 if self.numb else 1

    def compile(self, file=None):
        file.write('iconst_{}\n'.format(self.const))
        file.write('newarray {}\n'.format(self.type.split('[')[0] if self.type.split('[')[0] != 'string' else '[java/lang/String;'))
        if self.numb:
            for i in range(len(self.numb)):
                type = str(self.type)[0]
                file.write('dup\n')
                file.write('iconst_{}\n'.format(i))
                #tmp = LiteralNode(self.numb[i])
                self.numb[i].compile(file)
                file.write('{}astore\n'.format(type))

    def __str__(self):
        res = self.type + '{ '
        for it in self.numb:
            res += str(it.value)
            if it != self.numb[len(self.numb)-1]:
                res += ', '
            else:
                res += ' '
        res += '}'
        return res


class CallNode(ASTreeNode):
    def __init__(self, *args):
        self.constr = False
        self.print = False
        self.value = None
        self.args = None
        if args[0] == 'Console.WriteLine':
            self.print = True

            self.type = 'void'
            if len(args) > 1:
                self.args = args[1:]
            self.value = IdentNode(args[0])
            self.value.args = self.args
        else:
            self.constr = True if str(type(args[0])) != '<class \'ASTree.IdentNode\'>' else False
            self.value = args[1] if self.constr else args[0]
            if args[len(args)-1] != self.value:
                self.args = args[2:] if self.constr else args[1:]
            else:
                self.args = None
            self.value.args = self.args if self.args else ''
            self.type = self.value.value if self.constr else None
            self.static = False
            self.name = None

    @property
    def child(self)-> Tuple[ASTreeNode]:
        return self.value,#, self.args[0]

    def semantic(self, context: 'Context' = None):
        var = context.find_func(self.value, self.args)
        self.name = context.get_name()
        stack = 0
        if var is not None:
            self.static = var.static
            self.type = var.type #if var.constr else var.type.type
        if self.args:
            for param in self.args:
                stack += param.semantic(context)
        return stack + 1 if self.constr else stack

    def compile(self, file=None):
        paramtype = ''
        if self.args:
            if len(self.args) > 0:
                for it in self.args:
                    if '[' in it.type:
                        paramtype += '[L'
                    if str(it.type).split('[')[0] == 'string':
                        paramtype += 'java/lang/String;'
                    else:
                        paramtype += str(it.type)[0].upper()
        if self.constr:
            file.write('new {}\ndup\n'.format(self.value.value))
            if self.args and self.args != '':
                for it in self.args:
                    it.compile(file)
            file.write('invokespecial {}/<init>({})V\n'.format(self.value.value, paramtype))
        elif self.print:
            file.write('getstatic java/lang/System/out Ljava/io/PrintStream;\n')
            if self.args is not None:
                for it in self.args:
                    it.compile(file)
            file.write('invokevirtual java/io/PrintStream/println({})V\n'.format(paramtype))
        elif self.static:
            self.args[0].compile(file)
            file.write('invokestatic {}/{}({}){}\n'.format(self.name, self.value.value, str(self.args[0].type)[0].upper() if self.args else '',
                                                         str(self.type)[0].upper()))
        else:
            self.args[0].compile(file)
            file.write('invokevirtual {}/{}({}){}\n'.format(self.name, self.value.value, str(self.args[0].type)[0] if self.args else '', str(self.type)[0]))

    def strparam(self):
        return str(self.value) + '(' + str(self.args) + ')'

    def __str__(self):
        res = 'call'
        if self.type is not None:
            res += ' (dtype = {})'.format(self.type)
        return res


class ConsNode(ValueNode):
    def __init__(self, *param: Tuple[IdentNode]):
        self.param = param

    @property
    def child(self):
        return self.param

    def __str__(self):
        return ''


class FuncNode(ASTreeNode):
    def __init__(self, *args: Tuple[ASTreeNode]):#name: ASTreeNode, param: Tuple[IdentNode] = None, *args: Tuple[ASTreeNode]):
        self.locals = 0
        self.stack = 0
        self.access = args[0] if args[0] == 'public' or args[0] == 'private' else None
        self.static = None
        self.constr = False
        name = None
        if self.access:
            name = args[1]
        else:
            name = args[0]
        self.params = args[2] if self.access else args[1]
        self.block = args[3:] if self.access else args[2:]
        if str(type(name)) == '<class \'ASTree.VarNode\'>':
            self.type = name.type
            self.value = name.value
            self.access = name.access
            self.static = name.static
        elif str(type(name)) == '<class \'ASTree.IdentNode\'>':
            self.constr = True
            self.value = name.value
            self.type = name.value

    @staticmethod
    def parameters(params):
        res = ''
        for it in params.child:
            if res != '':
                res += ', '
            res += str(it.value.strparam())
        return res

    def semantic(self, context: Context = None):
        context.add_var(self)
        context = Context(context)
        for y in self.params.child:
            x = y.value
            x.var_type = VarType.Param
            context.add_var(x)
            context.add_par(x)
            x.index = context.get_index()
        for expr in self.block:
            self.stack += expr.semantic(context)
        self.stack += len(context.params)
        self.locals = len(context.vars)# - len(context.params)
        return 0

    def compile(self, file=None):
        paramtype = ''
        if len(self.params.child) > 0:
            for it in self.params.child:
                if '[' in it.type:
                    paramtype += '[L'
                if str(it.type).split('[')[0] == 'string':
                    paramtype += 'java/lang/String;'
                else:
                    paramtype += str(it.type)[0].upper()
        else:
            pass#paramtype = ''
        file.write('.method {} {} {}({}){}\n'.format(self.access if self.access else '', 'static' if self.static else '', self.value if not self.constr else '<init>',
                                                      paramtype,
                                                      str(self.type)[0].upper()
                                                      if not self.constr else 'V'))
        file.write('.limit stack {}\n'.format(self.stack))
        file.write('.limit locals {}\n'.format(self.locals))
        if self.constr:
            file.write('aload_0\ninvokespecial java/lang/Object/<init>(){}\n'.format(
                str(self.type)[0].upper()
                if not self.constr else 'V'))
        for expr in self.block:
            expr.compile(file)
        if len(self.block) > 0:
            if str(type(self.block[len(self.block) - 1])) != '<class \'ASTree.RetNode\'>':
                file.write('return\n')
        else:
            file.write('return\n')
        file.write('.end method\n\n')

    @property
    def child(self)->Tuple[ASTreeNode]:
        return self.block

    def __str__(self):
        res = '{} {} {} {}({})'.format(self.access if self.access else '', 'static' if self.static else '', self.type,
                                       self.value, self.parameters(self.params))
        if self.type:
            for x in self.params.child:
                it = x.value
                res += '(dtype = {}, vtype = {}, index = {})'.format(it.type, it.var_type, it.index)
        return res


class Class1Node(ASTreeNode):
    def __init__(self, *expr: Tuple[ASTreeNode]):
        self.access = expr[0] if str(type(expr[0])) != '<class \'ASTree.IdentNode\'>' else None
        self.value = expr[1].value if self.access is not None else expr[0].value
        self.block = expr[2:] if self.access is not None else expr[1:]

    def semantic(self, context: Context = None):
        context.name = self.value
        #context = Context(context)
        for it in self.block:
            it.semantic(context)

    def compile(self, file=None):
        file.write('.class {} {}\n'.format(self.access, self.value))
        file.write('.super java/lang/Object\n')
        for expr in self.block:
            expr.compile(file)

    @property
    def child(self)->Tuple[ASTreeNode]:
        return self.block

    def __str__(self):
        return '{} class {}'.format(self.access, str(self.value))


class ExprLinesNode(ASTreeNode):
    def __init__(self, *expr: ASTreeNode):
        super().__init__()
        self.expr = expr

    def compile(self, file=None):
        with open("file.j", 'w') as file:
            for it in self.expr:
                it.compile(file)

    def semantic(self, context: Context = None):
        context = Context(context)
        for it in self.expr:
            it.semantic(context)
        self.compile()
        return 0

    @property
    def child(self) -> Tuple[ASTreeNode, ...]:
        return self.expr

    def __str__(self)->str:
        return '!!!'