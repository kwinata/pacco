def show_help(commands, namespace, stream):
    max_len = max((len("pacco {} {}".format(namespace, c)) for c in commands)) + 1
    fmt = '  %-{}s'.format(max_len)
    for name in commands:
        appended_name = "pacco {} {}".format(namespace, name)
        print(fmt % appended_name, end="")
        stream.writeln(__format_docstring(commands[name].__doc__))
    stream.writeln("")
    stream.writeln("Pacco {} commands. Type 'pacco {} <command> -h' for help".format(namespace, namespace))


def __format_docstring(docstring):
    if not docstring:
        return ''
    docstring_lines = docstring.split('\n')
    data = []
    for line in docstring_lines:
        line = line.strip()
        data.append(line)
    return ' '.join(data)
