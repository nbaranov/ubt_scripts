import subprocess
import sys

def install_and_import(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

if __name__ == "__main__":
    install_and_import("urllib3")
    install_and_import("tqdm")
    install_and_import("requests")
    install_and_import("lxml")

