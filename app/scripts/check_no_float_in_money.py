import ast
import sys
from pathlib import Path

MONEY_PATHS = ["app/models", "app/schemas", "app/services", "app/repositories"]


# finds every use of the float type or a float literal in one file
def find_float_usages(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    usages = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "float":
            usages.append(f"{path}:{node.lineno}: `float` type is not allowed in money code")
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            usages.append(f"{path}:{node.lineno}: float literal {node.value!r} in money code")
    return usages


def main() -> int:
    usages = [
        usage
        for money_path in MONEY_PATHS
        for path in sorted(Path(money_path).rglob("*.py"))
        for usage in find_float_usages(path)
    ]
    for usage in usages:
        print(usage)
    if usages:
        print("Money must be integer minor units (int), never float.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
