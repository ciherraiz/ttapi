from enum import Enum

class SubscriptionType(str, Enum):
    """
    This is an :class:`~enum.Enum` that contains the subscription types for the alert streamer.
    """
    ACCOUNT = 'account-subscribe'  # 'account-subscribe' may be deprecated in the future
    HEARTBEAT = 'heartbeat'
    PUBLIC_WATCHLISTS = 'public-watchlists-subscribe'
    QUOTE_ALERTS = 'quote-alerts-subscribe'
    USER_MESSAGE = 'user-message-subscribe'