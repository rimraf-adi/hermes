from tree_sitter import Parser, Language
import tree_sitter_python as tspython


PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def parse()