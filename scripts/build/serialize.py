from typing import Any

from build.types import AnyNonProjFileInstance, FileInstance
from build.globals import global_tree
from build.paths import GEN_FOLDER, ROOT
from build.scan import get_project_from_project_path, get_projlink_from_project_path
from pathlib import Path
import json

def write_to_file(to_path: Path, output: dict[str, Any]) -> None:  # pyright: ignore[reportExplicitAny]
    to_path.parent.mkdir(exist_ok=True, parents=True)
    temp_path = to_path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)
        _ = file.write("\n")
    _ = temp_path.replace(to_path)

def serialize_global_tree() -> dict[str, object]:
    return {
        proj_id: {
            "name": entry.name,
            "datapath": str(entry.datapath.relative_to(ROOT)),
        }
        for proj_id, entry in global_tree.items()
    }

def write_global_tree() -> None:
    write_to_file(GEN_FOLDER/"global_tree.json", serialize_global_tree())

def serialize_projlink(projlink: FileInstance.ProjLink) -> dict[str, object]:
    return {
        "type": "projlink",
        "linkedid": projlink.linkedid,
        "name": projlink.name
    }

class SerializedProject:
    def __init__(self, id: str, data: dict[str, object]) -> None:
        self.id = id
        self.data = data
    id: str
    data: dict[str, object]


def serialize_project_data_list(projects: list[FileInstance.ProjectPath]) -> list[SerializedProject]:
    projects = projects.copy()
    def process_serialize_instance_data(instance: AnyNonProjFileInstance) -> dict[str, object]:
        if (isinstance(instance, FileInstance.DocFile)):
            return {
                "type": "docfile",
                "path": str(instance.data.path.relative_to(ROOT)),
                "mod_time": instance.data.mod_time.isoformat(),
                "headers": [ header.name for header in instance.headers ]
            }
        if (isinstance(instance, FileInstance.Folder)):
            return {
                "type": "folder",
                "path": str(instance.data.path.relative_to(ROOT)),
                "mod_time": instance.data.mod_time.isoformat(),
                "contents": [ process_serialize_instance_data(child) for child in instance.contents ]
            }
        if (isinstance(instance, FileInstance.ProjectPath)):
            projects.append(instance)
            temp_projlink: FileInstance.ProjLink = get_projlink_from_project_path(instance)
            return serialize_projlink(temp_projlink)
        if (isinstance(instance, FileInstance.ProjLink)):  # pyright: ignore[reportUnnecessaryIsInstance]
            return serialize_projlink(instance)
        raise TypeError("Unsupported instance type: " + type(instance).__name__)  # pyright: ignore[reportUnreachable]
    serialized: list[SerializedProject] = []
    index: int = 0
    while (index < projects.__len__()):
        project = projects[index]
        project = get_project_from_project_path(project)
        serialized_project: SerializedProject = SerializedProject(project.id, {})
        serialized_project.data = {
            "type": "project",
            "path": str(project.folder.data.path.relative_to(ROOT)),
            "mod_time": project.folder.data.mod_time.isoformat(),
            "icon": str(project.icon) if project.icon else None,
            "id": project.id,
            "contents": [ process_serialize_instance_data(instance) for instance in project.folder.contents ]
        }
        serialized.append(serialized_project)
        index += 1
    return serialized
def serialize_project_data(project: FileInstance.ProjectPath) -> list[SerializedProject]:
    return serialize_project_data_list([project])

def serialize_project_path_search(proj_path: FileInstance.ProjectPath) -> SerializedProject:
    return serialize_project_search(get_project_from_project_path(proj_path))
def serialize_project_search(project: FileInstance.Project) -> SerializedProject:
    serialized_project: SerializedProject = SerializedProject(project.id, {})

    headers: list[dict[str, object]] = []
    serialized_project.data["headers"] = headers

    def process_serialize_project_search(folder: FileInstance.Folder) -> None:
        for input in folder.contents:
            if (isinstance(input, FileInstance.Folder)):
                process_serialize_project_search(input)
            if (isinstance(input, FileInstance.DocFile)):
                for header in input.headers:
                    headers.append({
                            "name": header.name,
                            "alt_name": header.alt_name,
                            "significance": header.significance,
                            "contents": header.contents,
                            "path": str(input.data.path.relative_to(ROOT))
                        })


    process_serialize_project_search(project.folder)

    return serialized_project
