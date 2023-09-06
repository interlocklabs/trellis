from posthog import Posthog
import time
import os

def analyzer(name: str, _input: dict):
    if os.getenv("DISABLE_ANALYTICS") == 1:
        return
    else:
        Posthog(
            project_api_key="phc_qLInS8phhqhE7IrHTMxfbm5yBiTSLz30mOQmsrgLaCD",
            host="https://app.posthog.com",
        ).capture(str(int(time.time())), name, _input)
