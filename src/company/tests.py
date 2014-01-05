'''
Created on Jan 4, 2014

@author: terence
'''
from django.utils import unittest
from company.models import YearData, ItemAccount


class YearDataTest(unittest.TestCase):


    def setUp(self):
        self.data = YearData.objects.create(jan=10, feb=20, mar=30, apr=40, may=50, jun=60,
                                            jul=70, aug=80, sep=90, oct=100, nov=110, dec=120,
                                            account_id=1, account_type=ItemAccount.content_type(),
                                            year=2100)

    def tearDown(self):
        pass


    def testName(self):
        total = 0
        for month in range(1, 12):
            total += self.data.get(month)
            print total
        self.data.sum()
        self.assertTrue(total == self.data.total, "Computed: {} Actual: {}".format(total, self.data.total))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()