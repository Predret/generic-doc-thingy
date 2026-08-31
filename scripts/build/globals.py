from pathlib import Path

class ProjectNamePath:
    def __init__(self, name: str, datapath: Path) -> None:
        self.name = name
        self.datapath = datapath
    name: str
    datapath: Path

global_tree: dict[str, ProjectNamePath] = {}
