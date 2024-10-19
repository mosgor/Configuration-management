import json
import tarfile
import unittest

from main import execute_command, main, get_fl

class TestGui(unittest.TestCase):
    def setUp(self):
        main()
        self.main_files = get_fl()
        file = open("configuration.json")
        js = json.load(file)
        tar_file = js["vfs"]
        self.logs = js["test_log"]
        file.close()
        with tarfile.TarFile(tar_file, "r") as tar_ref:
            self.file_ls = tar_ref.getnames()

    def test_ls(self):
        self.main_files = get_fl()
        assert self.file_ls == self.main_files

    def test_cd(self):
        execute_command("cd 1", self.logs)
        self.main_files = get_fl()
        curr_files = self.file_ls
        name = "1"
        new_files = []
        for file in curr_files:
            if file.startswith(name) and file != name:
                new_files.append(file)
        assert self.main_files == new_files


if __name__ == '__main__':
    unittest.main()
