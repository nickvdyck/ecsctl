import os
import json

from os.path import exists
from pathlib import Path


class Config:
    def __init__(self):
        home = os.environ["HOME"]
        xdg_home = os.environ.get("XDG_CONFIG_HOME", f"{home}/.config")

        xdg_config_path = Path(f"{xdg_home}/ecs-ctl/config")
        home_path = Path(f"{home}/ecs-ctl/config")

        if xdg_config_path.exists():
            self.config_path = xdg_config_path
        elif home_path.exists():
            self.config_path = home_path
        else:
            self.config_path = xdg_config_path
            os.makedirs(f"{xdg_home}/ecs-ctl")
            with open(xdg_config_path, "w") as config_file:
                config_file.write("{}")
                config_file.flush()

        with open(self.config_path, "r") as config_file:
            file_data = config_file.read()
            data = json.loads(file_data)

            self.profile = data.get("profile", None)
            self.default_cluster = data.get("default_cluster", None)
            self.meets_ssm_prereqs = data.get("meets_ssm_prereqs", False)

    def set_profile(self, profile: str):
        self.profile = profile

    def set_default_cluster(self, default_cluster: str):
        self.default_cluster = default_cluster

    def set_meets_ssm_prereqs(self):
        self.meets_ssm_prereqs = True

    def save(self):
        with open(self.config_path, "w") as config_file:
            config_json = self.to_json()
            config_file.write(json.dumps(config_json))

    def to_json(self):
        return {
            "profile": self.profile,
            "default_cluster": self.default_cluster,
            "meets_ssm_prereqs": self.meets_ssm_prereqs,
        }
