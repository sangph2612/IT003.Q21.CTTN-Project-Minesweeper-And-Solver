import ast
import os
import re


def get_python_docstrings(filepath):
    docstrings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    if isinstance(node, ast.Module):
                        docstrings.append(f"Module:\n{docstring}")
                    elif isinstance(node, ast.ClassDef):
                        docstrings.append(f"Class {node.name}:\n{docstring}")
                    else:
                        docstrings.append(f"Function {node.name}:\n{docstring}")
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return docstrings


def get_cpp_docstrings(filepath):
    docstrings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.finditer(r'/\*\*[\s\S]*?\*/', content)
        for match in matches:
            docstrings.append(match.group(0))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return docstrings


def main():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(target_dir, 'docstring.txt')

    ignore_dirs = {'venv', '.env', 'env', '.git', '__pycache__', '.pytest_cache'}
    ignored_files = {'extract_docstrings.py'}

    with open(out_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith('.py') and file not in ignored_files:
                    docs = get_python_docstrings(filepath)
                    if docs:
                        out.write(f"=== {os.path.relpath(filepath, target_dir)} ===\n\n")
                        for d in docs:
                            out.write(f"{d}\n\n")
                        out.write('-' * 40 + '\n\n')
                elif file.endswith('.cpp') or file.endswith('.h'):
                    docs = get_cpp_docstrings(filepath)
                    if docs:
                        out.write(f"=== {os.path.relpath(filepath, target_dir)} ===\n\n")
                        for d in docs:
                            out.write(f"{d}\n\n")
                        out.write('-' * 40 + '\n\n')


if __name__ == '__main__':
    main()
