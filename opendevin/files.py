from pathlib import Path
from typing import Any, Dict, List


class File:
    name: str
    children: List["File"]

    def __init__(self, name: str, children: List["File"]):
        self.name = name
        self.children = children

    def to_dict(self) -> Dict[str, Any]:
        """Converts the File object to a dictionary.

        Returns:
            The dictionary representation of the File object.
        """
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children],
        }


def get_folder_structure(workdir: Path) -> File:
    """Gets the folder structure of a directory.

    Args:
        workdir: The directory path.

    Returns:
        The folder structure.
    """
    root = File(name=workdir.name, children=[])
    for item in workdir.iterdir():
        if item.is_dir():
            dir = get_folder_structure(item)
            if dir.children:
                root.children.append(dir)
        else:
            root.children.append(File(name=item.name, children=[]))
    return root
