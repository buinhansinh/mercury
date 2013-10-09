'''
Created on Feb 1, 2013

@author: terence
'''
from django.core.management.base import LabelCommand
from accounting.models import Bill
import sys
from company.models import TradeAccount


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


class Command(LabelCommand):
    
    def handle_label(self, label, **options):
        bill = Bill.objects.get(pk=label)
        answer = query_yes_no("Are you sure you want to delete Bill: {} Code: {}".format(bill.id, bill.code), 
                     default="no")
        if answer == "yes":
            account = bill.account()
            account.debt = account.debt - bill.total
            account.save()
            bill.delete()
            print "Deleted."
        else:
            print "Canceled."
        