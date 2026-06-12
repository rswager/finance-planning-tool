import os
from pathlib import Path

LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local")) / "finance-planning-tool"
SAVED_OBJECT_DATA = LOCAL_APP_DATA / "saved_objects"
