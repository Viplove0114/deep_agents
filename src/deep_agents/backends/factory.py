"""
Deep Agents — Backend Factory.

Provides a single ``create_backend()`` entry-point that returns the
appropriate backend object, extracted from notebook 3.

Supported backend types
-----------------------
* ``"state"``      → StateBackend (default, files live in LangGraph state)
* ``"filesystem"`` → FilesystemBackend (files on real disk)
* ``"store"``      → StoreBackend (files in a LangGraph store, cross-thread)
"""

from __future__ import annotations

from deepagents.backends import StateBackend, FilesystemBackend, StoreBackend
from langgraph.store.memory import InMemoryStore


# Display name → backend type key
BACKEND_OPTIONS: dict[str, str] = {
    "State (In-Memory)": "state",
    "Filesystem (Disk)": "filesystem",
    "Store (Cross-Thread)": "store",
}


def create_backend(
    backend_type: str = "state",
    *,
    root_dir: str = ".",
    virtual_mode: bool = True,
    namespace: tuple[str, ...] = ("default-user",),
):
    """
    Create and return a backend instance plus any companion objects.

    Parameters
    ----------
    backend_type : str
        One of ``"state"``, ``"filesystem"``, ``"store"``.
    root_dir : str
        Root directory for ``FilesystemBackend``.
    virtual_mode : bool
        Whether ``FilesystemBackend`` maps virtual paths onto *root_dir*.
    namespace : tuple[str, ...]
        Namespace tuple for ``StoreBackend``.

    Returns
    -------
    tuple[backend, store | None]
        A ``(backend_instance, store_or_none)`` pair.  The second element is
        only non-None for ``"store"`` backends.
    """
    if backend_type == "filesystem":
        return FilesystemBackend(root_dir=root_dir, virtual_mode=virtual_mode), None

    if backend_type == "store":
        store = InMemoryStore()
        ns = namespace  # capture for the lambda
        backend = StoreBackend(namespace=lambda _rt: ns)
        return backend, store

    # Default: StateBackend
    return StateBackend(), None
