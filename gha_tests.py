import os
import subprocess


def pylint_all() -> bool:
    files_to_check = ["top_level.py", "copier.py", "fantasy_football.py"]
    for root, dirs, files in os.walk("libs"):
        for dir_name in dirs:
            # Only one level deep
            if dir_name == "__pycache__":
                continue
            for file in os.listdir(os.path.join(root, dir_name)):
                if file.endswith(".py"):
                    files_to_check.append(os.path.join(root, dir_name, file))
        for file in files:
            if file.endswith(".py"):
                files_to_check.append(os.path.join(root, file))
    for file_path in files_to_check:
        print(f"Running pylint on {file_path}...")
        ret_val = subprocess.run(["pylint", file_path, "--disable=R0801"],
                                 capture_output=True, text=True)
        if "rated at 10.00/10" not in ret_val.stdout and len(ret_val.stdout) != 0:
            print(ret_val.stdout)
            return False
    return True


def gha_tests():
    print("")
    assert pylint_all()
    print("\r\nAll tests passed!\r\n")


if __name__ == "__main__":
    gha_tests()
