from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import TypeAlias





class FileInstance:
    class Header:
        def __init__(self, name: str, alt_name: str, significance: int, contents: str) -> None:
            self.name = name
            self.alt_name = alt_name
            self.significance = significance
            self.contents = contents
        name: str
        alt_name: str
        significance: int
        contents: str

    class Data:
        def __init__(self, path: Path, mod_time: datetime) -> None:
            self.path = path
            self.mod_time = mod_time
        path: Path
        mod_time: datetime
    class DocFile:
        def __init__(self, data: FileInstance.Data, headers: list[FileInstance.Header]) -> None:
            self.data = data
            self.headers = headers
        data: FileInstance.Data
        headers: list[FileInstance.Header]
    class Folder:
        def __init__(self, data: FileInstance.Data, contents: list[AnyNonProjFileInstance]) -> None:
            self.data = data
            self.contents = contents
        data: FileInstance.Data
        contents: list[AnyNonProjFileInstance]
    class Project:
        def __init__(self, folder: FileInstance.Folder, icon: Path | None, id: str) -> None:
            self.folder = folder
            self.icon = icon
            self.id = id
        folder: FileInstance.Folder
        icon: Path | None
        id: str
    class ProjLink:
        def __init__(self, linkedid: str, name: str) -> None:
            self.linkedid = linkedid
            self.name = name
        linkedid: str
        name: str
    class ProjectPath:
        def __init__(self, path: Path) -> None:
            self.path = path
        path: Path


AnyFileInstance: TypeAlias = FileInstance.DocFile | FileInstance.Folder | FileInstance.Project | FileInstance.ProjLink
AnyNonProjFileInstance: TypeAlias = FileInstance.DocFile | FileInstance.Folder | FileInstance.ProjectPath | FileInstance.ProjLink
