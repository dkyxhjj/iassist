import cv2
import time
import numpy as np
from collections import defaultdict, deque
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# Optional dependencies - import with error handling
try:
    from ultralytics import YOLO
    from ultralytics.utils.plotting import Annotator, colors
    YOLO_AVAILABLE = True
except ImportError:
    print("Warning: YOLO not available. Object detection will be disabled.")
    YOLO_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("Warning: Ollama not available. Some AI features will be disabled.")
    OLLAMA_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Warning: Groq not available. Some AI features will be disabled.")
    GROQ_AVAILABLE = False

try:
    import requests
except ImportError:
    print("Warning: Requests not available. Some features will be disabled.")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
