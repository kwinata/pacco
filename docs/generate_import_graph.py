import glob
import re


def get_python_files():
    return list(glob.glob("pacco/**/*.py", recursive=True))


def get_import_statements(file_object):
    import_lines = []
    for line in file_object:
        if re.match(r"import pacco\..*", line):
            import_lines.append(line)
        elif re.match(r"from pacco\..*", line):
            import_lines.append(line)
    return import_lines


def extract_import_statements(line: str):
    if re.match(r"import pacco\..*", line):
        return re.match(r"import (pacco(?:\.\w+)+)", line).group(1)
    elif re.match(r"from pacco\..*", line):
        match = re.match(r"from (pacco(?:\.\w+)+) import ((?:\w+\.)*(?:\w+))", line)
        return match.group(1)


def format_file_name(file_name: str):
    return re.sub(r"/", ".", file_name[:-3])


def main():
    files = get_python_files()
    print("digraph G {")
    print("  node [style=filled]; ratio = fill;")
    for file in files:
        if "test" in file:
            continue
        if "__init__" in file:
            continue
        import_statements = get_import_statements(open(file, "r"))
        for import_statement in import_statements:
            print('  "{}" -> "{}"'.format(
                format_file_name(file),
                extract_import_statements(import_statement)
            ), end=' [color="salmon2"];\n' if "utils.clients" in import_statement
                else '[color="cadetblue1"]\n' if "pacco/cli" in file else "\n")
        if "utils/clients" in file:
            print('  "{}" [color="salmon2"];'.format(format_file_name(file)))
        if "pacco/cli" in file:
            print('  "{}" [color="cadetblue1"];'.format(format_file_name(file)))

    print("}")



main()
