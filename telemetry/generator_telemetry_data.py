from datetime import datetime, timezone

import uuid
import time
import json

class Genereter_Telemetry_Data:
    def __init__(self,DeviceId):
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.data = {"name": "IDUX_ESTSClientTelemetryEvent_WebWatson",
            "time": self.timestamp,
            "ver": "4.0",
            "iKey": "o:b0c252808e614e949086e019ae1cb300",
            "ext": {
                "app": {
                    "ver": "2.1.19005.9",
                    "name": "IDUX_ESTSClientTelemetryEvent_WebWatson",
                    "sesId": uuid.uuid4().hex,
                    "userId": "p:1800",
                    "locale": "ar"
                },
                "cloud": {
                    "role": "SEC",
                    "roleInstance": "GV3XXXX",
                    "roleVer": "2.1.19005.9"
                },
                "sdk": {
                    "ver": "1DS-Web-JS-3.2.6",
                    "seq": 1,
                    "installId": DeviceId,
                    "epoch": str(int(time.time()))
                },
                "user": {
                    "locale": "ar"
                },
                "web": {
                    "domain": "login.microsoftonline.com",
                    "userConsent": False
                },
                "loc": {
                    "tz": "+03:00"
                }
            },
            "data": {
                "baseData": {
                    "properties": {
                        "version": ""
                    },
                    "viewId": 1,
                    "Data": json.dumps({
                        "pltMetrics": {
                            "apiTimingInfo": [],
                            "isPlt1": False,
                            "plt": 1747,
                            "timing": {
                                "navigationStart": int(time.time() * 1000),
                                "fetchStart": int(time.time() * 1000),
                                "domComplete": int(time.time() * 1000) + 2000,
                                "loadEventEnd": int(time.time() * 1000) + 2500
                            }
                        },
                        "ClientEvents": [
                            {"ID": 11008, "EventTime": int(time.time() * 1000), "Value": "Email_Phone_Skype_Entry", "DataViewID": "1"},
                            {"ID": 11009, "EventTime": int(time.time() * 1000) + 2000, "Value": "Submit", "DataViewID": "1"}
                        ]
                    }),
                    "ServerPageID": "1104",
                    "PageName": "ConvergedSignIn",
                    "ServiceID": "3",
                    "CorrelationId": str(uuid.uuid4())
                }
            }
        }
    def return_value(self):
        return self.data