import os, sys
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, basedir)
os.environ["DISABLE_SENTRY"] = "1"