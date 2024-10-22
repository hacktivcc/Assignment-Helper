import uuid
import time
from datetime import datetime, timezone

class CookieGenerator:
    def __init__(self, telemetry_device_id):
        self.MicrosoftApplicationsTelemetryDeviceId = telemetry_device_id

    def generate_initial_cookies(self):
        session_id = uuid.uuid4().hex
        acquisition_date = int(time.time() * 1000)
        renewal_date = acquisition_date + 1800000
        ai_session = f"{session_id}|{acquisition_date}|{renewal_date}"
        
        user_id = uuid.uuid4().hex
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        ai_user = f"{user_id}|{timestamp}"
        
        telemetry_device_id = self.MicrosoftApplicationsTelemetryDeviceId
        
        return (f"ai_user={ai_user}; ai_session={ai_session}; "
                f"MicrosoftApplicationsTelemetryDeviceId={telemetry_device_id};")