from posthog import Posthog
from dotenv import load_dotenv
import time
import os

load_dotenv()
p = Posthog(
    project_api_key="phc_qLInS8phhqhE7IrHTMxfbm5yBiTSLz30mOQmsrgLaCD",
    host="https://app.posthog.com",
)

def analyzer(name: str, _input: dict):
    if os.getenv("DISABLE_TELEMETRY") == 1:
        return
    else:
        p.capture(str(int(time.time())), name, _input)
