from datetime import datetime

Time = datetime
"""Type for time used across the whole module. 

We have it as alias so we can easily change that in the future.
"""


def now() -> Time:
    """Returns current Time."""
    return datetime.utcnow()
