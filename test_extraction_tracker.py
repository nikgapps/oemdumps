import unittest
from unittest.mock import Mock

import requests

from extraction_tracker import ExtractionTracker


def response(status=200, data=None):
    result = Mock(status_code=status)
    result.json.return_value = data
    if status >= 400:
        result.raise_for_status.side_effect = requests.HTTPError(str(status))
    return result


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.tracker = ExtractionTracker("test-token", self.session)

    def test_completed_filename_is_reused(self):
        record = {"status": "complete", "sourceFilename": "ota.zip", "dumpProject": "17_kodiak_260905"}
        self.session.get.return_value = response(data=record)
        self.assertEqual(self.tracker.lookup("ota.zip"), record)

    def test_missing_record_creates_completion_commit(self):
        self.session.get.side_effect = [response(404), response(data={}), response(data={"default_branch": "main"})]
        self.session.post.return_value = response(data={})
        record = self.tracker.mark("ota.zip", "https://example.test/ota.zip", "17_kodiak_260905",
                                   "17", "kodiak", "fingerprint", ["product", "system"])
        payload = self.session.post.call_args.kwargs["json"]
        self.assertEqual(payload["branch"], "main")
        self.assertEqual(payload["actions"][0]["action"], "create")
        self.assertEqual(record["partitions"], ["product", "system"])

    def test_inaccessible_project_is_not_a_cache_miss(self):
        self.session.get.side_effect = [response(404), response(403)]
        with self.assertRaises(requests.HTTPError):
            self.tracker.lookup("ota.zip")

    def test_existing_record_is_not_republished(self):
        record = {"status": "complete", "sourceFilename": "ota.zip", "dumpProject": "dump"}
        self.session.get.return_value = response(data=record)
        self.tracker.mark("ota.zip", "url", "dump", "17", "kodiak", "fp", ["product"])
        self.session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
