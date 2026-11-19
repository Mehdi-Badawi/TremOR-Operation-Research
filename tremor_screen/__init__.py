"""TremOR tap-screening research prototype (public reference implementation)."""

from tremor_screen.features import TapFeatures, detect_taps, extract_features
from tremor_screen.model import ScreeningModel, ZoneResult
from tremor_screen.splits import grouped_split

__all__ = [
    "TapFeatures",
    "detect_taps",
    "extract_features",
    "ScreeningModel",
    "ZoneResult",
    "grouped_split",
]
__version__ = "0.1.0"
