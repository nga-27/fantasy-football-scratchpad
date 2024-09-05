"""copier.py

So we can copy the league output to a shared drive!
"""
import os
import shutil
from dotenv import load_dotenv


PWD = os.path.dirname(__file__)
# PWD_FUNC, _ = os.path.split(PWD)
PWD_FUNC = PWD
DOTENV_PATH = os.path.join(PWD_FUNC, '.env')
if not os.path.exists(DOTENV_PATH):
    print(f'WARNING: NO ENVIRONMENT FILE. Current PWD: {DOTENV_PATH}')

load_dotenv(DOTENV_PATH)

SOURCE_PATH = os.getenv("INPUT_SOURCE_PATH", "")
DEST_PATH = os.getenv("SHARE_DIRECTORY_PATH", "")


def league_copier():
    """league_copier

    Since shell commands (such as "cp") are apparently terrible with paths, we'll do it in python!
    """
    # print(SOURCE_PATH, DEST_PATH)
    shutil.copy(SOURCE_PATH, DEST_PATH)

league_copier()
