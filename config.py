import os

# Global variables
CURRENT_RESULTS_FOLDER = None

def init():
    """Initialize global variables with default values"""
    global CURRENT_RESULTS_FOLDER
    CURRENT_RESULTS_FOLDER = None