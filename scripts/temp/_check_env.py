import sys
print("python", sys.version)
try:
    import tensorflow as tf
    print("tensorflow", tf.__version__)
except Exception as e:
    print("tensorflow MISSING:", e)
try:
    import numpy as np
    print("numpy", np.__version__)
except Exception as e:
    print("numpy MISSING:", e)
try:
    import h5py
    print("h5py", h5py.__version__)
except Exception as e:
    print("h5py MISSING:", e)
try:
    import sklearn
    print("sklearn", sklearn.__version__)
except Exception as e:
    print("sklearn MISSING:", e)
try:
    import mediapipe as mp
    print("mediapipe", mp.__version__)
except Exception as e:
    print("mediapipe MISSING:", e)
try:
    import cv2
    print("cv2", cv2.__version__)
except Exception as e:
    print("cv2 MISSING:", e)
