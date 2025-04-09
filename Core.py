"""
Core classes for pattern drafting system.
This module provides the foundation for defining, manipulating, and rendering clothing patterns.
"""
import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union, Callable
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, FancyArrowPatch
