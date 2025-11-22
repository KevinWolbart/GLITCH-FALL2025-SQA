
import unittest
import importlib.util
import os
import tempfile

# Dynamically import git.repo.miner.py as miner
import sys
import pathlib
module_path = pathlib.Path(__file__).parent / 'git.repo.miner.py'
spec = importlib.util.spec_from_file_location('miner', str(module_path))
miner = importlib.util.module_from_spec(spec)
sys.modules['miner'] = miner
spec.loader.exec_module(miner)

class TestGitRepoMiner(unittest.TestCase):
    def test_makeChunks(self):
        data = [1, 2, 3, 4, 5]
        chunks = list(miner.makeChunks(data, 2))
        self.assertEqual(chunks, [[1, 2], [3, 4], [5]])

    def test_dumpContentIntoFile(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            miner.dumpContentIntoFile('hello', tf.name)
            tf.close()
            with open(tf.name) as f:
                content = f.read()
            os.unlink(tf.name)
        self.assertEqual(content, 'hello')

    def test_getPythonCount_empty(self):
        with tempfile.TemporaryDirectory() as d:
            count = miner.getPythonCount(d)
            self.assertEqual(count, 0)

    def test_deleteRepo_success(self):
        with tempfile.TemporaryDirectory() as d:
            # Create a file inside to ensure directory exists
            with open(os.path.join(d, 'file.txt'), 'w') as f:
                f.write('data')
            # Should delete directory and log success
            miner.deleteRepo(d, 'TEST')
            self.assertFalse(os.path.exists(d))

    def test_deleteRepo_not_found(self):
        # Should not raise error if directory does not exist
        d = tempfile.mkdtemp()
        os.rmdir(d)
        miner.deleteRepo(d, 'TEST')
        self.assertFalse(os.path.exists(d))

    def test_getMLLibraryUsage(self):
        with tempfile.TemporaryDirectory() as d:
            pyfile = os.path.join(d, 'ml.py')
            with open(pyfile, 'w') as f:
                f.write('import sklearn\nimport torch\n')
            count = miner.getMLLibraryUsage(d)
            self.assertGreaterEqual(count, 2)

    def test_getMLStats(self):
        with tempfile.TemporaryDirectory() as d:
            # Create two repo dirs, each with a .py file using ML libs
            repo1 = os.path.join(d, 'repo1')
            repo2 = os.path.join(d, 'repo2')
            os.mkdir(repo1)
            os.mkdir(repo2)
            with open(os.path.join(repo1, 'a.py'), 'w') as f:
                f.write('import sklearn')
            with open(os.path.join(repo2, 'b.py'), 'w') as f:
                f.write('import torch')
            stats = miner.getMLStats(d)
            self.assertEqual(len(stats), 2)
            self.assertTrue(any(count > 0 for _, count in stats))


if __name__ == '__main__':
    unittest.main()
