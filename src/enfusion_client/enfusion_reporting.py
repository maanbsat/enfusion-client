from datetime import date
from typing import Optional

import requests
import pandas as pd

HOSTNAME_PROD = "webservices.enfusionsystems.com"
HOSTNAME_QA = "webservices-qa.enfusionsystems.com"


class EnfusionReportingError(Exception):
    pass


class EnfusionReporting:
    def __init__(self, username: str, password: str, hostname=HOSTNAME_PROD):
        self._username = username
        self._hostname = hostname
        self._session = requests.Session()
        res = self._session.get(
            f"https://{hostname}/auth/authentication/generateSecureAPIToken",
            auth=(username, password),
        )
        if res.status_code != 200:
            raise EnfusionReportingError(res.text)
        self._token = res.text
        self._session.headers["Authorization"] = "Bearer " + self._token

    # Call the Enfusion API to get a report, and convert to
    # a Pandas DataFrame
    def get_raw_report(self, report_path: str, **kwargs):
        parameters = {"report": report_path}
        # Add all custom report parameters
        parameters.update(kwargs)
        for k, v in parameters.items():
            # format dates appropriately
            if isinstance(v, date):
                parameters[k] = v.strftime("%m/%d/%Y")
        res = self._session.get(
            f"https://{self._hostname}/api/reports", params=parameters
        )
        if res.status_code != 200:
            raise EnfusionReportingError(res.text)
        return res.json()

    # Call the Enfusion API to get a report, and convert to
    # a Pandas DataFrame. Returns None if report is empty
    def get_report(self, report_path: str, **kwargs) -> Optional[pd.DataFrame]:
        res = self.get_raw_report(
            report_path, includeMetaData=True, includeTotals=False, **kwargs
        )
        # Convert the JSON response to an array of dicts
        rows = [{k: v["value"] for k, v in r.items()} for r in res["rows"]]
        df = pd.DataFrame(rows)
        if len(df) < 1:
            return None
        for col in res["tableMetadata"]["columns"]:
            if col["dataType"] == "Date":
                df[col["name"]] = pd.to_datetime(df[col["name"]])
            elif col["dataType"] == "Integer":
                df[col["name"]] = df[col["name"]].astype("UInt64")
        return df
