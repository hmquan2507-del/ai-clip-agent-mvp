from __future__ import annotations


class ProductWorkspaceError(RuntimeError):
    pass


class ProductWorkspaceNotFoundError(
    ProductWorkspaceError
):
    pass


class ProductWorkspaceLoadError(
    ProductWorkspaceError
):
    pass