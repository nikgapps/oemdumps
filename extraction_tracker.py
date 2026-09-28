"""Track completed OEM publications in the nikgapps/tracker repository."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from urllib.parse import quote

import requests


class ExtractionTracker:
    def __init__(self, token=None, session=None):
        token = token or os.environ.get("GITLAB_TOKEN")
        if not token:
            raise ValueError("GITLAB_TOKEN is required")
        self.session = session or requests.Session()
        self.session.headers.update({"PRIVATE-TOKEN": token})
        self.project_url = "https://gitlab.com/api/v4/projects/" + quote("nikgapps/tracker", safe="")

    @staticmethod
    def record_path(filename):
        if not filename or "/" in filename or "\\" in filename:
            raise ValueError("A source filename without directory components is required")
        digest = hashlib.sha256(filename.encode("utf-8")).hexdigest()
        return f"extractions/{digest}.json"

    def lookup(self, filename):
        path = quote(self.record_path(filename), safe="")
        response = self.session.get(
            f"{self.project_url}/repository/files/{path}/raw",
            params={"ref": "HEAD"}, timeout=60,
        )
        if response.status_code == 404:
            # Distinguish a missing record from an inaccessible tracker project.
            project = self.session.get(self.project_url, timeout=60)
            project.raise_for_status()
            return None
        response.raise_for_status()
        record = response.json()
        if record.get("status") != "complete" or record.get("sourceFilename") != filename:
            raise ValueError("Invalid extraction completion record")
        return record

    def mark(self, filename, source_url, dump_project, android_version, device, fingerprint, partitions):
        existing = self.lookup(filename)
        if existing:
            return existing
        response = self.session.get(self.project_url, timeout=60)
        response.raise_for_status()
        branch = response.json().get("default_branch") or "main"
        record = {
            "schemaVersion": 1, "status": "complete",
            "sourceFilename": filename, "sourceUrl": source_url,
            "dumpProject": dump_project, "androidVersion": android_version,
            "device": device, "fingerprint": fingerprint,
            "partitions": sorted(partitions),
            "completedAt": datetime.now(timezone.utc).isoformat(),
        }
        response = self.session.post(
            f"{self.project_url}/repository/commits",
            json={"branch": branch, "commit_message": f"Record extraction of {filename}",
                  "actions": [{"action": "create", "file_path": self.record_path(filename),
                               "content": json.dumps(record, indent=2) + "\n"}]},
            timeout=60,
        )
        response.raise_for_status()
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check"])
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    try:
        record = ExtractionTracker().lookup(args.filename)
        if record is None:
            print(f"No completed extraction for {args.filename}")
            return 1
        print(f"Already extracted {args.filename}: {record['dumpProject']}")
        return 0
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"Tracker check failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
