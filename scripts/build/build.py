from __future__ import annotations

import json
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from time import perf_counter
from typing import TypeAlias, override

HERE = Path(__file__).resolve()
ROOT = (HERE.parent/Path("../..")).resolve()
DOC_FOLDER: Path = (HERE.parent/Path("../../html/docs")).resolve()
GEN_FOLDER: Path = ROOT/"generated"
OUTPUT: Path = GEN_FOLDER/"tree.json"

PROJECT_FOLDER: Path = OUTPUT/"project"
SEARCH_FOLDER: Path = OUTPUT/"search"

MAX_SEARCH_FILE_BYTE = 1024 * 1024

if (not ROOT.is_dir()):
    raise RuntimeError("Root folder is not present!")
if (not DOC_FOLDER.is_dir()):
    raise RuntimeError("Documentation folder is not present!")



class FileInstance:
    class Data:
        def __init__(self, path: Path, mod_time: datetime) -> None:
            self.path = path
            self.mod_time = mod_time
        path: Path
        mod_time: datetime
    class DocFile:
        def __init__(self, data: FileInstance.Data, headers: list[str]) -> None:
            self.data = data
            self.headers = headers
        data: FileInstance.Data
        headers: list[str]
    class Folder:
        def __init__(self, data: FileInstance.Data, contents: list[AnyFileInstance]) -> None:
            self.data = data
            self.contents = contents
        data: FileInstance.Data
        contents: list[AnyFileInstance]
    class Project:
        def __init__(self, folder: FileInstance.Folder, icon: Path | None) -> None:
            self.folder = folder
            self.icon = icon
        folder: FileInstance.Folder
        icon: Path | None

AnyFileInstance: TypeAlias = FileInstance.DocFile | FileInstance.Folder | FileInstance.Project

def get_filedata(path: Path) -> FileInstance.Data:
    mod_time = datetime.fromtimestamp(path.stat().st_mtime).astimezone(UTC)
    data = FileInstance.Data(path=path, mod_time=mod_time)
    return data
def get_icon_helper(path: Path) -> Path | None:
    try:
        with path.open("r", encoding="utf-8") as file:
            data: object = json.load(file) #pyright: ignore[reportAny]
    except json.JSONDecodeError:
        return None
    except OSError:
        return None
    if not isinstance(data, dict):
        return None
    icon: object = data.get("icon") #pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if not isinstance(icon, str):
        return None
    else: return (ROOT/Path(icon))
def get_icon(path: Path) -> Path | None:
    icon = get_icon_helper(path)
    if (not icon):
       print(f"Icon is invalid in file: {path}")
    elif (not icon.is_file()):
       print(f"Icon from {path} is gives an invalid path: {icon}")
    return icon

class DocHeaderParser(HTMLParser):
    def __init__(self, file_path: Path) -> None:
        super().__init__()
        self.file_path = file_path
        self.names = []
    file_path: Path
    names: list[str]

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if (tag != "doc-header"):
            return
        attributes = dict(attrs)
        name = attributes.get("name")

        if (name is None or not name.strip()):
            print("Warning. Doc header's name is null in path " + str(self.file_path) + "Skipping it.")
            return
        self.names.append(name)

def get_doc_headers(path: Path) -> list[str]:
    parser = DocHeaderParser(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            for chunk in iter(lambda: file.read(64*1024), ""):
                parser.feed(chunk)
    except (OSError, UnicodeDecodeError) as error:
        print(f"Warning: could not read {path}: {error}")
        return []
    parser.close()
    return parser.names

def get_docfile(path: Path) -> FileInstance.DocFile:
    data = get_filedata(path)
    headers = get_doc_headers(path)
    return FileInstance.DocFile(data, headers)


def scan_directories(folder: FileInstance.Folder) -> None:
    for file_instance in folder.data.path.iterdir():
        if (file_instance.is_file()):
            if (file_instance.suffix != ".html"):
                continue
            doc_file: FileInstance.DocFile = get_docfile(file_instance)
            folder.data.mod_time = max(folder.data.mod_time, doc_file.data.mod_time)
            folder.contents.append(doc_file)
        elif (file_instance.is_dir()):
            if (file_instance.is_symlink()):
                print("Warning: a folder symlink detected!")
                continue
            data = get_filedata(file_instance)
            subfolder = FileInstance.Folder(data=data, contents=[])
            scan_directories(subfolder)
            folder.data.mod_time = max(folder.data.mod_time, subfolder.data.mod_time)
            proj_folder = subfolder.data.path/Path("_proj.json")
            if (proj_folder.is_file()):
                icon = get_icon(proj_folder)
                proj = FileInstance.Project(folder=subfolder, icon=icon)
                folder.contents.append(proj)
                continue

            folder.contents.append(subfolder)

def get_root_folder() -> FileInstance.Folder:
    data = FileInstance.Data(path=DOC_FOLDER, mod_time=datetime.min.replace(tzinfo=UTC))
    return FileInstance.Folder(data, [])

def debug_folders_scan(folder: FileInstance.Folder) -> str:
    to_print: str = ""
    for file_instance in folder.contents:
        if (isinstance(file_instance, FileInstance.DocFile)):
            to_print += "DocFile: " + str(file_instance.data.path) + "mod: " + str(file_instance.data.mod_time) + "\n"
        if (isinstance(file_instance, FileInstance.Folder)):
            to_print += "Folder: " + str(file_instance.data.path) + "mod: " + str(file_instance.data.mod_time) + "\n"
            to_print += debug_folders_scan(file_instance)
            to_print += "endfolder: " + str(file_instance.data.path.name) + "\n"
        if (isinstance(file_instance, FileInstance.Project)):
            to_print += "Project: " + str(file_instance.folder.data.path) + "icon: " + str(file_instance.icon) + "mod: " + str(file_instance.folder.data.mod_time) + "\n"
            to_print += debug_folders_scan(file_instance.folder)
            to_print += "endproj: " + str(file_instance.folder.data.path.name) + "\n"
    return to_print

def serialize_instance(instance: AnyFileInstance) -> dict[str, object]:
    if (isinstance(instance, FileInstance.DocFile)):
        return {
            "type": "docfile",
            "path": str(instance.data.path.relative_to(ROOT)),
            "mod_time": instance.data.mod_time.isoformat(),
            "headers": instance.headers
        }
    if (isinstance(instance, FileInstance.Folder)):
        return {
            "type": "folder",
            "path": str(instance.data.path.relative_to(ROOT)),
            "mod_time": instance.data.mod_time.isoformat(),
            "contents": [ serialize_instance(child) for child in instance.contents ]
        }
    # if (isinstance(instance, FileInstance.Project)):
    return {
        "type": "project",
        "path": str(instance.folder.data.path.relative_to(ROOT)),
        "mod_time": instance.folder.data.mod_time.isoformat(),
        "icon": str(instance.icon.relative_to(ROOT)) if instance.icon else None,
        "contents": [ serialize_instance(child) for child in instance.folder.contents ]
    }
def write_output() -> None:
    GEN_FOLDER.mkdir(exist_ok=True, parents=True)
    output = {
        "root": serialize_instance(doc_folder)
    }
    temp_path = OUTPUT.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)
        _ = file.write("\n")
    _ = temp_path.replace(OUTPUT)

start_build = perf_counter()
doc_folder = get_root_folder()
scan_directories(doc_folder)
after_scan = perf_counter()
elapsed = after_scan - start_build
print("Finished scanning directories in " + format(elapsed, ".6f") + " seconds.")
print(serialize_instance(doc_folder))
after_serialize = perf_counter()
elapsed = after_serialize - after_scan
print("Finished serializing in " + format(elapsed, ".6f") + " seconds.")
write_output()
# test push
