from pathlib import Path

HERE = Path(__file__).resolve()

ROOT = (HERE.parent/Path("../..")).resolve()
DOC_FOLDER: Path = (ROOT/Path("html/docs"))
GEN_FOLDER: Path = ROOT/"generated"


PROJECT_FOLDER: Path = GEN_FOLDER/"project"
SEARCH_FOLDER: Path = GEN_FOLDER/"search"

MAX_SEARCH_FILE_BYTE = 1024 * 1024
