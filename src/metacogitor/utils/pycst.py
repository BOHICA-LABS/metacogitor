"""Utilities for working with the Python Concrete Syntax Tree (CST)."""
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Union

import libcst as cst
from libcst._nodes.module import Module

DocstringNode = Union[cst.Module, cst.ClassDef, cst.FunctionDef]


def get_docstring_statement(body: DocstringNode) -> cst.SimpleStatementLine:
    """Extracts the docstring from the body of a node.

    :param body: The body of a node.
    :type body: DocstringNode
    :return: The docstring statement if it exists, None otherwise.
    :rtype: cst.SimpleStatementLine
    """

    if isinstance(body, cst.Module):
        body = body.body
    else:
        body = body.body.body

    if not body:
        return

    statement = body[0]
    if not isinstance(statement, cst.SimpleStatementLine):
        return

    expr = statement
    while isinstance(expr, (cst.BaseSuite, cst.SimpleStatementLine)):
        if len(expr.body) == 0:
            return None
        expr = expr.body[0]

    if not isinstance(expr, cst.Expr):
        return None

    val = expr.value
    if not isinstance(val, (cst.SimpleString, cst.ConcatenatedString)):
        return None

    evaluated_value = val.evaluated_value
    if isinstance(evaluated_value, bytes):
        return None

    return statement


class DocstringCollector(cst.CSTVisitor):
    """A visitor class for collecting docstrings from a CST."""

    def __init__(self):
        """Initialize the visitor.

        :param stack: A list to keep track of the current path in the CST.
        :type stack: list[str]
        :param docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
        :type docstrings: dict[tuple[str, ...], cst.SimpleStatementLine]
        """

        self.stack: list[str] = []
        self.docstrings: dict[tuple[str, ...], cst.SimpleStatementLine] = {}

    def visit_Module(self, node: cst.Module) -> bool | None:
        """Visit a Module node.

        :param node: The Module node to visit.
        :type node: cst.Module
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """
        self.stack.append("")

    def leave_Module(self, node: cst.Module) -> None:
        """Leave a Module node.

        :param node: The Module node to leave.
        :type node: cst.Module
        :return: None
        :rtype: None
        """

        return self._leave(node)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:
        """Visit a ClassDef node.

        :param node: The ClassDef node to visit.
        :type node: cst.ClassDef
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """

        self.stack.append(node.name.value)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """Leave a ClassDef node.

        :param node: The ClassDef node to leave.
        :type node: cst.ClassDef
        :return: None
        :rtype: None
        """

        return self._leave(node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:
        """Visit a FunctionDef node.

        :param node: The FunctionDef node to visit.
        :type node: cst.FunctionDef
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """

        self.stack.append(node.name.value)

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Leave a FunctionDef node.

        :param node: The FunctionDef node to leave.
        :type node: cst.FunctionDef
        :return: None
        :rtype: None
        """

        return self._leave(node)

    def _leave(self, node: DocstringNode) -> None:
        """Leave a node.

        :param node: The node to leave.
        :type node: DocstringNode
        :return: None
        :rtype: None
        """

        key = tuple(self.stack)
        self.stack.pop()
        if hasattr(node, "decorators") and any(
            i.decorator.value == "overload" for i in node.decorators
        ):
            return

        statement = get_docstring_statement(node)
        if statement:
            self.docstrings[key] = statement


class DocstringTransformer(cst.CSTTransformer):
    """A transformer class for replacing docstrings in a CST.

    Attributes:
        stack: A list to keep track of the current path in the CST.
        docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
    """

    def __init__(
        self,
        docstrings: dict[tuple[str, ...], cst.SimpleStatementLine],
    ):
        """Initialize the transformer.
        :param docstrings: A dictionary mapping paths in the CST to their corresponding docstrings.
        :type docstrings: dict[tuple[str, ...], cst.SimpleStatementLine]
        """

        self.stack: list[str] = []
        self.docstrings = docstrings

    def visit_Module(self, node: cst.Module) -> bool | None:
        """Visit a Module node.

        :param node: The Module node to visit.
        :type node: cst.Module
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """

        self.stack.append("")

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        """Leave a Module node.

        :param original_node: The original Module node.
        :type original_node: Module
        :param updated_node: The updated Module node.
        :type updated_node: Module
        :return: The updated Module node.
        :rtype: Module
        """

        return self._leave(original_node, updated_node)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:
        """Visit a ClassDef node.

        :param node: The ClassDef node to visit.
        :type node: cst.ClassDef
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """

        self.stack.append(node.name.value)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        """Leave a ClassDef node.

        :param original_node: The original ClassDef node.
        :type original_node: ClassDef
        :param updated_node: The updated ClassDef node.
        :type updated_node: ClassDef
        :return: The updated ClassDef node.
        :rtype: ClassDef
        """

        return self._leave(original_node, updated_node)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:
        """Visit a FunctionDef node.

        :param node: The FunctionDef node to visit.
        :type node: cst.FunctionDef
        :return: True if the node's children should be visited, False if not, or None if the visitor should use the
                 default visit behavior.
        :rtype: bool | None
        """

        self.stack.append(node.name.value)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        """Leave a FunctionDef node.

        :param original_node: The original FunctionDef node.
        :type original_node: FunctionDef
        :param updated_node: The updated FunctionDef node.
        :type updated_node: FunctionDef
        :return: The updated FunctionDef node.
        :rtype: FunctionDef
        """

        return self._leave(original_node, updated_node)

    def _leave(
        self, original_node: DocstringNode, updated_node: DocstringNode
    ) -> DocstringNode:
        """Leave a node.

        :param original_node: The original node.
        :type original_node: DocstringNode
        :param updated_node: The updated node.
        :type updated_node: DocstringNode
        :return: The updated node.
        :rtype: DocstringNode
        """

        key = tuple(self.stack)
        self.stack.pop()

        if hasattr(updated_node, "decorators") and any(
            (i.decorator.value == "overload") for i in updated_node.decorators
        ):
            return updated_node

        statement = self.docstrings.get(key)
        if not statement:
            return updated_node

        original_statement = get_docstring_statement(original_node)

        if isinstance(updated_node, cst.Module):
            body = updated_node.body
            if original_statement:
                return updated_node.with_changes(body=(statement, *body[1:]))
            else:
                updated_node = updated_node.with_changes(
                    body=(statement, cst.EmptyLine(), *body)
                )
                return updated_node

        body = (
            updated_node.body.body[1:] if original_statement else updated_node.body.body
        )
        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=(statement, *body))
        )


def merge_docstring(code: str, documented_code: str) -> str:
    """Merges the docstrings from the documented code into the original code.

    :param code: The original code.
    :type code: str
    :param documented_code: The documented code.
    :type documented_code: str
    :return: The original code with the docstrings from the documented code.
    :rtype: str
    """

    code_tree = cst.parse_module(code)
    documented_code_tree = cst.parse_module(documented_code)

    visitor = DocstringCollector()
    documented_code_tree.visit(visitor)
    transformer = DocstringTransformer(visitor.docstrings)
    modified_tree = code_tree.visit(transformer)
    return modified_tree.code
