"""Validate panel export structure and parse embedded scripts without executing them."""
import json
from pathlib import Path
import re
import subprocess

import yaml


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate(egg):
    version = egg["meta"]["version"]
    assert version in {"PTDL_v2", "PLCN_v1", "PLCN_v2", "PLCN_v3"}, version
    assert isinstance(egg["name"], str) and egg["name"]
    assert isinstance(egg["docker_images"], dict) and egg["docker_images"]
    assert egg.get("startup") or egg.get("startup_commands"), "Missing startup command"
    for key in ("files", "startup", "logs"):
        value = egg["config"][key]
        if isinstance(value, str):
            json.loads(value, object_pairs_hook=unique_object)
        else:
            assert isinstance(value, dict), f"Invalid config.{key}"
    variables = egg["variables"]
    names = [variable["env_variable"] for variable in variables]
    assert len(names) == len(set(names)), "Duplicate environment variable"
    assert all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) for name in names)
    for script in egg["scripts"].values():
        if script is None:
            continue
        entrypoint = script["entrypoint"]
        assert entrypoint in {"bash", "/bin/bash", "ash", "/bin/ash"}, entrypoint
        command = (["busybox", "ash", "-n"] if entrypoint.endswith("ash") and
                   not entrypoint.endswith("bash") else ["bash", "-O", "extglob", "-n"])
        # Wings normalizes panel-export CRLF before writing the installation script.
        result = subprocess.run(command, input=script["script"].replace("\r\n", "\n"),
                                text=True, capture_output=True)
        assert result.returncode == 0, result.stderr


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    eggs = 0
    errors = []
    for name in filter(None, files):
        path = Path(name)
        try:
            if path.suffix == ".json":
                data = json.loads(path.read_text(), object_pairs_hook=unique_object)
            elif path.suffix in {".yml", ".yaml"}:
                data = yaml.safe_load(path.read_text())
            elif path.suffix == ".sh":
                subprocess.run(["bash", "-n", str(path)], check=True)
                continue
            else:
                continue
            if isinstance(data, dict) and isinstance(data.get("meta"), dict):
                validate(data)
                eggs += 1
        except (AssertionError, KeyError, TypeError, ValueError, yaml.YAMLError,
                subprocess.CalledProcessError) as error:
            errors.append(f"{name}: {error}")
    assert eggs > 0, "No panel exports were checked"
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {eggs} exports, JSON/YAML data and embedded shell syntax")


if __name__ == "__main__":
    main()
