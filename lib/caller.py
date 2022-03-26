
import subprocess

subprocess.Popen(["venv/bin/python3.9", "pixelate_runner.py", "../test-images/input/teddy.jpeg", "../test-images/output/pix-teddy.png"]).wait()
