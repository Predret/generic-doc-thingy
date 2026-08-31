from datetime import UTC, datetime
from html.parser import HTMLParser
import json
from pathlib import Path
from typing import override

from build.types import FileInstance
from scripts.build.paths import ROOT


class DocHeaderParser(HTMLParser):
    HEADER_TAG: str = "doc-header"
    CONTENT_TAGS: list[str] = ["p", "span"]

    def __init__(self, file_path: Path) -> None:
        super().__init__()
        self.file_path = file_path
        self.headers: list[FileInstance.Header] = []
        self.intro_contents: str = ""
        self._in_header: bool = False
        self._in_content_tag: bool = False
        self._current: FileInstance.Header | None = None
    file_path: Path

    def on_pre_header_data(self, data: str) -> None:
        self.intro_contents += data

    def make_header(self, attributes: dict[str, str | None]) -> FileInstance.Header | None:
            name = attributes.get("name")
            if (name is None or not name.strip()):
                print(f"Warning. Doc header's name is null in path {self.file_path}. Skipping it.")
                return None
            size_raw = attributes.get("size")
            significance = int(size_raw) if (size_raw is not None and size_raw.strip().isdigit()) else 0
            return FileInstance.Header(name=name, alt_name="", significance=significance, contents="")


    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if (tag == self.HEADER_TAG):
            header = self.make_header(dict(attrs))
            if (header is None):
                raise RuntimeWarning("Warning: A header's name is invalid in " + str(self.file_path))
            self._current = header
            self.headers.append(header)
            self._in_header = True
        if (tag in self.CONTENT_TAGS):
            self._in_content_tag = True

    @override
    def handle_endtag(self, tag: str):
        if (tag == self.HEADER_TAG):
            self._in_header = False
            return
        if (tag in self.CONTENT_TAGS):
            self._in_content_tag = False

    @override
    def handle_data(self, data: str):
        if (self._in_header):
            if (self._current is not None):
                self._current.alt_name += data
            return
        if (not self._in_content_tag):
            return
        if (self._current is None):
            self.on_pre_header_data(data)
        else:
            self._current.contents += data

def get_doc_headers(path: Path) -> list[FileInstance.Header]:
    parser = DocHeaderParser(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            for chunk in iter(lambda: file.read(64*1024), ""):
                parser.feed(chunk)
    except (OSError, UnicodeDecodeError) as error:
        print(f"Warning: could not read {path}: {error}")
        return []
    parser.close()
    return parser.headers

def get_docfile(path: Path) -> FileInstance.DocFile:
    data = get_filedata(path)
    headers = get_doc_headers(path)
    return FileInstance.DocFile(data, headers)

def get_filedata(path: Path) -> FileInstance.Data:
    mod_time = datetime.fromtimestamp(path.stat().st_mtime).astimezone(UTC)
    data = FileInstance.Data(path=path, mod_time=mod_time)
    return data
def get_projlink_from_path(folder: Path) -> FileInstance.ProjLink:
    proj_file = folder/Path("_proj.json")
    if (not proj_file.is_file()):
        raise RuntimeError("Failed to find _proj.json in " + str(folder))
    with proj_file.open("r", encoding="utf-8") as file:
        data = json.load(file)  # pyright: ignore[reportAny]
    if (not isinstance(data, dict)):
        raise RuntimeError("Project file has invalid formatting!")
    project_id = data.get("id")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    if (not isinstance(project_id, str)):
        raise RuntimeError("Failed to get ID from project")
    return FileInstance.ProjLink(linkedid=project_id, name=folder.name)
def get_projlink_from_project_path(proj_path: FileInstance.ProjectPath) -> FileInstance.ProjLink:
    return get_projlink_from_path(proj_path.path)
def scan_folder(path: Path) -> FileInstance.Folder:
    folder: FileInstance.Folder = FileInstance.Folder(data=get_filedata(path), contents=[])
    for file_instance in path.iterdir():
        if (file_instance.is_file()):
            if (file_instance.suffix != ".html"):
                continue
            doc_file: FileInstance.DocFile = get_docfile(file_instance)
            folder.data.mod_time = max(folder.data.mod_time, doc_file.data.mod_time)
            folder.contents.append(doc_file)
        elif (file_instance.is_dir()):
            if (file_instance.is_symlink()):
                print("Warning: a folder symlink detected! Skipping.")
                continue
            proj_file = file_instance/Path("_proj.json")
            if (proj_file.is_file()):
                project_path: FileInstance.ProjectPath = FileInstance.ProjectPath(path=file_instance)
                folder.contents.append(project_path)
                continue
            subfolder = scan_folder(file_instance)
            folder.data.mod_time = max(folder.data.mod_time, subfolder.data.mod_time)
            folder.contents.append(subfolder)
    return folder

def get_project_from_path(folder: Path) -> FileInstance.Project:
    proj_file = folder/Path("_proj.json")
    if (not proj_file.is_file()):
        raise RuntimeError("Failed to find _proj.json in " + str(folder))
    with proj_file.open("r", encoding="utf-8") as file:
        data = json.load(file)  # pyright: ignore[reportAny]
    if (not isinstance(data, dict)):
        raise RuntimeError("Project file has invalid formatting!")
    icon = data.get("icon")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if (not isinstance(icon, str)):
        icon = None
    else:
        icon = (ROOT/Path(icon)).resolve().relative_to(ROOT)
    project_id = data.get("id")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if (not isinstance(project_id, str)):
        raise RuntimeError("Failed to get ID from project")
    project: FileInstance.Project = FileInstance.Project(scan_folder(folder), Path(icon) if (icon is not None) else None, project_id)
    return project

def get_project_from_project_path(proj_path: FileInstance.ProjectPath) -> FileInstance.Project:
    return get_project_from_path(proj_path.path)
