from itertools import islice
from pathlib import Path
from typing import Any, List

MAX_DIRECTORIES_TO_RETURN = 1000


class WorkspaceFile:
    name: str
    children: list['WorkspaceFile']

    def __init__(self, name: str, children: list['WorkspaceFile']):
        self.name = name
        self.children = children

    def to_dict(self) -> dict[str, Any]:
        """Converts the File object to a dictionary.

        Returns:
            The dictionary representation of the File object.
        """
        return {
            'name': self.name,
            'children': [child.to_dict() for child in self.children],
        }


def get_folder_structure(workdir: Path) -> WorkspaceFile:
    """Gets the folder structure of a directory.

    Args:
        workdir: The directory path.

    Returns:
        The folder structure.
    """
    root = WorkspaceFile(name=workdir.name, children=[])
    for item in workdir.iterdir():
        if item.is_dir():
            dir = get_folder_structure(item)
            if dir.children:
                root.children.append(dir)
        else:
            root.children.append(WorkspaceFile(name=item.name, children=[]))
    return root


def get_subdirectories(workdir: Path) -> List[Path]:
    """Gets the list of (immediate) child directories under the given directory.
       At most MAX_DIRECTORIES_TO_RETURN subdirectories are returned.

    Args:
      workdir (Path): The directory path to search for subdirectories.

    Returns:
        A list of Path objects representing the immediate children.
    """
    return list(
        islice(
            (item for item in workdir.iterdir() if item.is_dir()),
            MAX_DIRECTORIES_TO_RETURN,
        )
    )
