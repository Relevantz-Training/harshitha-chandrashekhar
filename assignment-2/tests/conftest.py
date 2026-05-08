import sys, os
# Make the project root importable when pytest is run from the tests/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
