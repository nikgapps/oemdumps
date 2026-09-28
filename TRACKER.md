# Completed extractions

`run.sh` resolves the OTA filename, then queries `nikgapps/tracker` before
downloading or extracting it. A matching completion record skips extraction
and exits successfully. A missing record proceeds normally; API errors stop
the run rather than starting a duplicate extraction.

`upload_to_gitlab.py` creates the record after publishing all detected,
non-skipped partitions. Records are JSON files under `extractions/`, named by
the SHA-256 of the original ZIP filename. They include the original URL,
filename, dump project, Android version, device, fingerprint, partitions, and
completion timestamp. The existing `GITLAB_TOKEN` needs write access to tracker.

Manual lookup:

```text
python extraction_tracker.py check --filename OTA_FILENAME.zip
```

Exit codes: 0 = completed, 1 = missing, 2 = tracker error.

Older dumps without a completion record are not automatically reused. The
current extraction validation behavior is unchanged; this records successful
publication of the existing extraction path, not a full extraction audit.

Deploy the Python files to the repository cloned by `run.sh` and rebuild the
container once for the updated `run.sh`. No tracker writes happen during local
unit tests.
