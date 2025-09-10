from tree_sitter import Parser, Language
import tree_sitter_python as tspython
import sys
import json
from typing import List, Dict, Any


PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def extract_chunks(source_code: bytes, root_node) -> List[Dict[str, Any]]:
    """
    Extract semantic chunks (functions and classes) from the syntax tree.
    Returns a list of dicts with: kind, name, start_line, end_line, text.
    """
    chunks: List[Dict[str, Any]] = []

    def visit(node):
        is_func = node.type == "function_definition"
        is_class = node.type == "class_definition"
        if is_func or is_class:
            name_node = node.child_by_field_name("name")
            name = None
            if name_node is not None:
                name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")

            text = source_code[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
            chunks.append(
                {
                    "kind": "function" if is_func else "class",
                    "name": name,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "text": text,
                }
            )

        for child in node.children:
            visit(child)

    visit(root_node)
    # If no functions/classes, fall back to module-level chunk
    if not chunks:
        text = source_code.decode("utf-8", errors="replace")
        chunks.append(
            {
                "kind": "module",
                "name": None,
                "start_line": 1,
                "end_line": root_node.end_point[0] + 1,
                "text": text,
            }
        )
    return chunks


def main(argv: List[str]) -> int:
    # Read source from file path arg or stdin
    if len(argv) > 1 and argv[1] != "-":
        file_path = argv[1]
        with open(file_path, "rb") as f:
            source = f.read()
        source_label = file_path
    else:
        source = sys.stdin.buffer.read()
        source_label = "<stdin>"

    tree = parser.parse(source)
    root = tree.root_node

    chunks = extract_chunks(source, root)

    output = {
        "source": source_label,
        "chunks": [
            {
                "kind": c["kind"],
                "name": c["name"],
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "text": c["text"],
            }
            for c in chunks
        ],
    }

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))