"""Location for all filepaths needed for application"""

from pathlib import Path

from platformdirs import user_data_dir

LOCAL_APP_DATA = Path(user_data_dir("finance_planning_tool", "SABRS"))
SAVED_OBJECT_DATA = LOCAL_APP_DATA / "saved_objects"
