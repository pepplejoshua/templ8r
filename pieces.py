from inspect import isfunction
import re

init = {
    "int": int,
    "float": float,
}

INDENT_STEP = 4

class CodeBuilder:
    def __init__(cb, indent: int = 0) -> None:
        cb.indentLevel = indent
        cb.code = []

    def add_line(cb, line: str):
        cb.code.extend([" "*cb.indentLevel, line, "\n"])

    def indent(cb):
        cb.indentLevel += INDENT_STEP
    
    def dedent(cb):
        cb.indentLevel -= INDENT_STEP

    def add_section(cb):
        section = CodeBuilder(cb.indentLevel)
        cb.code.append(section)
        return section

    def __str__(cb) -> str:
        return "".join(str(c) for c in cb.code)

    # execute the code and return all the globals it references
    def extractGlobals(cb) -> dict:
        # make sure we finished all started code blocks
        assert cb.indentLevel == 0
        py_source = str(cb)

        globalNamespace = {}
        exec(py_source, globalNamespace)
        return globalNamespace

class Templ8rSyntaxError(Exception):
    pass

class Templ8r:
    def __init__(t, template: str, *contexts) -> None:
        t.context = {}
        for cDict in contexts:
            t.context.update(cDict)

        t.all_vars = set()
        t.loop_vars = set()

        code = CodeBuilder()

        code.add_line("# Welcome to an auto generated python file!")
        code.add_line("def renderer(context: dict, do_dots):")
        code.indent()
        
        # this is where we take the templated variable names
        # and make them available in the code
        vars_code = code.add_section()
        
        code.add_line("result = []")
        code.add_line("append_to_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("make_str = str")
         
        # these 2 work together to push buffered code pieces to the result array
        buffered = []
        def flush_output():
            if len(buffered) == 1:
                code.add_line(f"append_to_result({buffered[0]})")
            elif len(buffered) > 1:
                code.add_line(f"extend_result([{', '.join(buffered)}])")
            # delete the contents of buffered
            del buffered[:]

        ops_stack: list[str] = []

        template_tokens = re.split(r"(?s)({.*?}|{%.*?%}|{#.*?#})", template)

        for token in template_tokens:
            if token.startswith("{#"):
                # ignore comments
                continue
            elif token.startswith("{%"):
                # expr = token[2:-2].strip()
                # we've run into an action tag (logic tag or loop tag)
                # so we write everything in the buffer out first
                flush_output()

                words = token[2:-2].strip().split()

                op  = words[0]

                if op == "if":
                    # if expressions are of form:
                    # {% if someVarName %}
                    if len(words) != 2:
                        t._syntax_error("Can't understand if:", token)
                    
                    ops_stack.append(op)
                    operand = words[1]
                    code.add_line(f"if {t._to_expr_code(operand)}:")
                    code.indent()
                elif op == "for":
                    # for expressions are of form:
                    # {% for loopVar in loopAble %}
                    # loopAble can have . references
                    if len(words) != 4 or words[2] != "in":
                        t._syntax_error("Can't understand for:", token)

                    ops_stack.append(op)
                    loopVar = words[1]   
                    t._check_variable(loopVar, t.loop_vars)
                    loopAble = t._to_expr_code(words[3])
                    code.add_line(f"for c_{loopVar} in {loopAble}:")
                    code.indent()
                elif op.startswith("end"):
                    # we are trying to end an operation, 
                    # so an operation of a matching type has to be on ops_stack
                    # {% endWHAT %}
                    if len(words) != 1:
                        t._syntax_error("Can't understand end:", token)
                    end_what = op[3:]
                    if not ops_stack:
                        t._syntax_error("Too many ends:", token)
                    started = ops_stack.pop()
                    if started != end_what:
                        t._syntax_error("Mismatched end:", end_what)
                    code.dedent()
                else:
                    t._syntax_error("Don't understand tag:", op)
            elif token.startswith("{"):
                expr = t._to_expr_code(token[1:-1].strip())
                buffered.append(f"make_str({expr})")
            else:
                if token:
                    buffered.append(repr(token))
        
        if ops_stack:
            t._syntax_error("Unhandled action tag:", ops_stack[-1])
        
        flush_output()

        for var_name in t.all_vars - t.loop_vars:
            vars_code.add_line(f"c_{var_name} = context[{repr(var_name)}]")
        
        code.add_line(f"return ''.join(result)")
        code.dedent()
        t.source = str(code)

        # we grab the function we just finished composing
        t._composed_renderer = code.extractGlobals()["renderer"]
        # and use it for all future renders of the template
    
    def _to_expr_code(t, expr: str):
        code = ""
        if "|" in expr:
            pipes = expr.split("|")
            code = t._to_expr_code(pipes[0])
            for fn in pipes[1:]:
                t._check_variable(fn, t.all_vars)
                code = f"c_{fn}({code})"
        elif "." in expr:
            dots = expr.split(".")
            code = t._to_expr_code(dots[0])
            args = ', '.join(repr(dot) for dot in dots[1:])
            code = f"do_dots({code}, {args})"
        else:
            t._check_variable(expr, t.all_vars)
            code = f"c_{expr}"
        return code

    def _check_variable(t, name, vars_set: set):
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            t._syntax_error("Not a valid name", name)
        vars_set.add(name)
    
    def _syntax_error(t, msg: str, thing):
        raise Templ8rSyntaxError(f"{msg}: {repr(thing)}")
    
    def _do_dots(_, value, *dots):
        for dot in dots:
            try:
                val = getattr(value, dot)
            except AttributeError:
                val = value[dot]
            if callable(value) or isfunction(value):
                val = value()
        return val

    def render(t, additionalContext: dict = None):
        render_context = dict(t.context)
        if additionalContext:
            render_context.update(additionalContext)

        return t._composed_renderer(render_context, t._do_dots)