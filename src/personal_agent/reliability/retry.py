import time
import random
from typing import Callable, Tuple, Any, Dict, Optional

def retry_with_backoff(
    func: Callable[[], Any],
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    jitter: bool = True
) -> Tuple[bool, Any, Dict[str, Any]]:
    """Executes func with exponential backoff and random jitter retries."""
    attempt = 0
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        try:
            res = func()
            metadata = {
                "attempt_count": attempt,
                "retry_count": attempt - 1,
                "last_error": None,
                "status": "SUCCESS"
            }
            return True, res, metadata
        except Exception as e:
            last_error = str(e)
            if attempt >= max_attempts:
                break
            
            # Calculate exponential backoff delay: base * (2 ** (attempt - 1))
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if jitter:
                delay = delay * (0.5 + random.random())
            
            time.sleep(delay)

    metadata = {
        "attempt_count": attempt,
        "retry_count": attempt - 1,
        "last_error": last_error,
        "status": "FAILED"
    }
    return False, last_error, metadata
