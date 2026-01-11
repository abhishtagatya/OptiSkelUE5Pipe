import sys, importlib, unreal, os

script_path = "C:\\Users\\abhis\\Development\\OptiTrack\\OptiSkelUE5Pipe\\Unreal"
script_dir = os.path.join(unreal.Paths.project_dir(), script_path)
if script_dir not in sys.path:
    sys.path.append(script_dir)

"""
import automate_asset as autoasset
importlib.reload(autoasset)
autoasset.auto_skm_to_ikr(skm)
"""