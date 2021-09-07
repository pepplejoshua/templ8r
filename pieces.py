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

class Templ8r:
    def __init__(t, template: str, *contexts) -> None:
        t.contexts = {}
        for cDict in contexts:
            t.contexts.update(cDict)

        t.reg_vars = set()
        t.loop_vars = set()

        code = CodeBuilder()

        code.add_line("# Welcome to an auto generated python file!")
        code.add_line("def render_function(context: dict, do_dots):")
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
                code.add_line(f"append_to_result({', '.join(buffered)})")
            # delete the contents of buffered
            del buffered[:]

        ops_stack: list[str]
        
