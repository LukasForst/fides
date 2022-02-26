from enum import Enum


# TODO: [!] check this evaluation

class Satisfaction(Enum):
    """Represents value how much was client satisfied with the interaction
    0 <= satisfaction <= 1
    where 0 is NOT satisfied and 1 is satisfied
    """
    ERROR = 0
    UNSURE = 0.5
    OK = 1


class Weight(Enum):
    """How much was the interaction important.
    0 <= weight <= 1
    where 0 is unimportant and 1 is important
    """
    FIRST_ENCOUNTER = 0.1
    PING = 0.2
    INTELLIGENCE_NO_DATA_REPORT = 0.3
    INTELLIGENCE_REQUEST = 0.5
    ALERT = 0.7
    RECOMMENDATION_REQUEST = 0.7
    INTELLIGENCE_DATA_REPORT = 1
    RECOMMENDATION_RESPONSE = 1
    ERROR = 1
