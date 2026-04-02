"""Configuration constants for Device Farm"""


class DeviceFarmConfig:
    """Centralized configuration for Device Farm operations.

    Note: AWS Device Farm is only available in us-west-2 region.
    The region is hardcoded in DeviceFarmClient and cannot be changed.
    """

    # Polling Configuration
    POLL_INTERVAL_SECONDS = 2
    """How often to check upload/session status (seconds)"""

    UPLOAD_POLL_ATTEMPTS = 30
    """Maximum number of polling attempts for uploads"""

    RUN_POLL_INTERVAL_SECONDS = 30
    """How often to check test run status (seconds)"""

    # Timeout Configuration
    MAX_WAIT_SECONDS = 300
    """Maximum wait time for session setup (5 minutes - under Device Farm's inactivity timeout)"""

    RUN_TIMEOUT_SECONDS = 1800
    """Maximum test run duration (30 minutes)"""
