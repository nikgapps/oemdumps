import tempfile
import unittest
from pathlib import Path

from helper.FileOp import FileOp


class RepoInfoTests(unittest.TestCase):
    @staticmethod
    def write_properties(root, folder, partition, device, complete=True):
        path = root / folder / "build.prop"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = (f"ro.product.{partition}.device={device}\n"
                f"ro.product.{partition}.brand=google\n"
                f"ro.{partition}.build.fingerprint=google/{device}/{device}:17/CD1A.260905.001.B1/id:user/release-keys\n")
        if complete:
            text += f"ro.{partition}.build.version.release=17\nro.{partition}.build.date.utc=1788307200\n"
        path.write_text(text, encoding="utf-8")

    def test_product_wins_over_generic_system(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_properties(root, "system/system/system", "system", "generic")
            self.write_properties(root, "system_ext/system_ext/etc", "system_ext", "other")
            self.write_properties(root, "product/product/etc", "product", "kodiak")
            version, _, device, brand, fingerprint = FileOp.get_repo_info(root)
            self.assertEqual((version, device, brand), ("17", "kodiak", "google"))
            self.assertIn("google/kodiak/kodiak", fingerprint)

    def test_system_fills_missing_fields_without_overwriting_product(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_properties(root, "product/etc", "product", "kodiak", complete=False)
            self.write_properties(root, "system/system", "system", "generic")
            version, _, device, _, fingerprint = FileOp.get_repo_info(root)
            self.assertEqual((version, device), ("17", "kodiak"))
            self.assertIn("google/kodiak/kodiak", fingerprint)


if __name__ == "__main__":
    unittest.main()
