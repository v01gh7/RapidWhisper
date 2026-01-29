"""
Pytest configuration and fixtures for RapidWhisper tests.
"""

from hypothesis import settings, HealthCheck

# Configure Hypothesis for property-based testing
# Minimum 100 iterations for each property test as per design document
settings.register_profile(
    "rapidwhisper",
    max_examples=100,
    deadline=None,  # Disable deadline for audio/API tests
    suppress_health_check=[HealthCheck.too_slow]
)

# Load the profile
settings.load_profile("rapidwhisper")
