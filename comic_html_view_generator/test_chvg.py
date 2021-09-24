import unittest
from os import path
from random import sample

from .chvg import mirror_unzip_cbz, sort_nicely


class TestMirrorUnzipCBZ(unittest.TestCase):
    def setUp(self):
        pass

    def testExtractOdd(self):
        basepath = path.dirname(path.abspath(__file__))
        testfile = 'simulated_comic_volume_001.cbz'
        testfpath = path.join(basepath, testfile)

        testout = path.join(basepath, 'test_output_volume')
        print('input folder:', basepath)
        print('output dir  :', testout)
        mirror_unzip_cbz(basepath, testout, verbose=True)


class TestSortNicely(unittest.TestCase):
    def testSortPurenums(self):
        lst = ['1', '2', '3', '10', '11', '20', '31']
        nice_lst = sort_nicely(sample(lst, k=len(lst)))
        assert lst == nice_lst

    def testSortLettersandNums(self):
        lst = ['a1', 'a2', 'a3', 'a10', 'a11', 'a20', 'a31']
        nice_lst = sort_nicely(sample(lst, k=len(lst)))
        assert lst == nice_lst

    def testPaddedLettersandNums(self):
        lst = ['a01', 'a02', 'a03', 'a10', 'a11', 'a20', 'a31']
        nice_lst = sort_nicely(sample(lst, k=len(lst)))
        assert lst == nice_lst


if __name__ == '__main__':
    unittest.main()
