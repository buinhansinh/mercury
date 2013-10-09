'''
Created on Aug 30, 2012

@author: bratface
'''
from django.utils import unittest
from addressbook.models import Contact
from common.models import Enum


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def testQuery(self):
        contact = Contact.objects.create(name="Test1")
        contact.label(Enum('gone'))
        contact.save()
        self.assertTrue(contact.labels.filter(name=Enum('gone')).exists())

    def tearDown(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()