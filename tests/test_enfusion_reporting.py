import unittest
import os

import dotenv

from enfusion_reporting import EnfusionReporting

dotenv.load_dotenv()

class TestEnfusionReporting(unittest.TestCase):
    def setUp(self):
        self._client = EnfusionReporting(os.environ["ENFN_USERNAME"], os.environ["ENFN_PASSWORD"])

    def test_get_report(self):
        self._client.get_report(os.environ["ENFN_TEST_REPORT_PATH"])
        return True

if __name__ == "__main__":
    unittest.main()
