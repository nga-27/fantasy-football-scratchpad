import os
import shutil
from dotenv import load_dotenv


PWD = os.path.dirname(__file__)
PWD_FUNC, _ = os.path.split(PWD)
DOTENV_PATH = os.path.join(PWD_FUNC, '.env')
if os.path.exists(DOTENV_PATH) is False:
    print(f'WARNING: NO ENVIRONMENT FILE. Current PWD: {DOTENV_PATH}')

load_dotenv(DOTENV_PATH)

def league_copier():
    SOURCE_PATH = os.getenv("INPUT_SOURCE_PATH", "")
    DEST_PATH = os.getenv("SHARE_DIRECTORY_PATH", "")
    # print(SOURCE_PATH, DEST_PATH)
    shutil.copy(SOURCE_PATH, DEST_PATH)

league_copier()