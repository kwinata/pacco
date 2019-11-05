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


def is_skipped(file):
    return "test" in file or "__init__" in file


def format_line(file, import_statement):
    if "utils.clients" in import_statement:
        return '[color="salmon2"];'
    if "pacco/cli" in file:
        return '[color="cadetblue1"]'
    return ''


def add_node_formatting(file):
    if "utils/clients" in file:
        print('  "{}" [color="salmon2"];'.format(format_file_name(file)))
    if "pacco/cli" in file:
        print('  "{}" [color="cadetblue1"];'.format(format_file_name(file)))


def main():
    files = [file for file in get_python_files() if not(is_skipped(file))]
    print("digraph G {")
    print("  node [style=filled]; ratio = fill;")
    for file in files:
        import_statements = get_import_statements(open(file, "r"))
        for import_statement in import_statements:
            print('  "{}" -> "{}"'.format(
                format_file_name(file),
                extract_import_statements(import_statement)
            ), end=format_line(file, import_statement)+'\n')
        add_node_formatting(file)
    print("}")


main()
