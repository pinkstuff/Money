#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""Python Bank Statement Project
can be used interactively or as a standalone app.
Looks through a santander text based statement
and trys to give a more logical breakdown of what
has been spent"""


import re
import datetime
import time
import sys
import csv
import argparse


### Exception Classes

class BadFile(Exception):
    """This exception is raised when the script cant
    understand the statement file supplied to it"""
    pass

class RecordError(Exception):
    """This exception is raised when a record cant
    be parsed. Most likely a bug but could be a previously
    unknown transaction layout"""
    pass


### Application Classes

class Transaction(object):
    """Base Transaction Class: All bank statement records
    inherret from inherit from here"""
    
    def __init__(self):
        """constructor, initialises everything to None"""

        self._date = None
        self._amount = None
        self._description = None
        self._timestamp = None
        self._trans_type = None
        self._place = None
        self._balance = None
        
    def __repr__(self):
        return self._description

    
    def extract_data(self):
        """Once the transaction type is set this will use the regex's
        in trans_regex_map to extract the name of the place or 
        person in the transaction and the date if is given in the
        description"""
  
        # game over if the transaction type has not been set
        if self._trans_type is None:
            raise Exception("trans_type needs to be set first")
        
        # looks to see if we have the regex before trying to match
        if self._trans_type in self._trans_regex_map:
            match = re.match(self._trans_regex_map[self._trans_type],
                             self._description, 
                             re.I|re.VERBOSE) 
                
            if match is not None:
                # looks like we have found a match
                extraction_dict = match.groupdict()
                self.set_place(extraction_dict['place'])
                if 'date' in extraction_dict and extraction_dict['date']:
                    self.set_date(extraction_dict['date'])

            else:
                # No match? either bug or new transaction pattern: BAIL OUT
                msg = "Trying to Parse:\n{}\n".format(self._description)
                msg += "With: {}".format(self._trans_regex_map[self._trans_type])
                raise RecordError(msg)
            
    
    def set_date(self, date_string):
        """sets the date, attempts to use the date in the
        description if it is available. Otherwise revert to one in 
        statement"""

       # check correct type
        if type(date_string) is not str:
            msg = "date_string needs to be str\n"
            msg += "got {} instead"
            raise TypeError(msg.format(type(date_string)))
        
        date_string = date_string.strip(" \t\xa0")
        
       
       # which date do we have dd-mm-yy, dd-mm-yyyy or even
       # yyyy-mm-dd
        date_patterns = (r"""(?P<day>\d{2})[/-]
                            (?P<month>\d{2})[/-]
                            (?P<year>\d{2}|\d{4})$""",

                          r"""(?P<year>\d{4})[/-]
                            (?P<month>\d{2})[/-]
                            (?P<day>\d{2})$""")
        
        for pattern in date_patterns:
            date = re.match(pattern, date_string, re.VERBOSE)

            if date:
                # BOOM its either on of the three above
                d = int(date.groupdict()['day'])
                m = int(date.groupdict()['month'])
                y = date.groupdict()['year']
                if len(y) == 2:
                    y = '20' + y
                y = int(y)
                self._date = datetime.datetime(y, m, d)
                return 0

        # maybe its dd-mmm eg "21JAN"
        if re.match(r"^\d{2}\w{3}$", date_string):
             date = re.match(r"^(?P<day>\d{2})(?P<month>\w{3})$", date_string)
             d = date.groupdict()['day']
             m = date.groupdict()['month']
             # just use the year in the statement
             y = str(self._date.year)
             self._date = datetime.strptime(d+m+y, '%d%b%y')
             return 0
       
        # nothing works but we still have the date in the statement
        elif self._date:
            return 0
   
        # no date in the statement and a bad description
        # things dont look good
        else: 
            msg = "I have no idea what that date is\n" 
            msg += date_string
            raise RecordError(msg)
    

    def set_place(self, place_string):
        """Sets the name of person or business we have paid.
        firstly we check the type"""

        # TODO maybe we need a seperate place class so we can
        # fix things like store numbers and weird names

        if type(place_string) is not str:
            msg = "place_string needs to be str\n"
            msg += "got {} instead"
            raise TypeError(msg.format(type(place_string)))

        # not sure why theres HTML & escape in here, weird
        place_string = place_string.replace('&amp;', 'and')
        self._place = place_string

    
    def set_amount(self, amount_string):
        """Sets the amount a transaction was, Takes out annoying
        whitespaces and currency codes like GBP"""

        if type(amount_string) is not str:
            msg = "amount_string needs to be str\n"
            msg += "got {} instead"
            raise TypeError(msg.format(type(date_string)))
        
        amount_string = amount_string.strip(" \xa0\tGBP") 
        self._amount = float(amount_string)

    def get_place(self):
        """returns the place"""

        # TODO, will be more useful when there is a seperate
        # place class

        return self._place

    
    def get_description(self):
        """returns the initial description"""

        # Not sure im happy with the description in
        # the statement. Its a little ugly
        # good enough for now
        
        return self._description


    def get_date(self, format="%d-%m-%Y"):
        """returns the strftime of the date %s for unix timestamp
        useful for sorting"""
        
        # Unashamedly hard coding British date format
        return self._date.strftime(format)


    def get_amount(self):
        """returns the amount a transaction costed"""

        # might add pound symbol or something in the future
        return self._amount


class Santander(Transaction):
    """Class for creating santander statement record objects"""


    def __init__(self, description, date, amount, balance):
        """constructor"""
        
        super(Santander, self).__init__()
        
        self._description = description
        self._balance = balance
        self._account = 'Santander'
        self.set_date(date)
        self.set_amount(amount)
        
        # the trans regex map pretty much powers this whole script
        # See unit tests to see example of matches

        self._trans_regex_map = \
        {'Bill Payment' : 
         r"""^bill\ payment                 # Trans Type (link word 'to')
         \s(via\ faster\ payment\ )?to      # Sometimes via faster payments!
         \s(?P<place>.+?)                   # Grab who Ive paid
         [ ,]{0,3}(reference\ \w*)?         # reference 
         [ ,]{0,3}(mandate\ no\ \d{0,3})?$  # or mandate or both""",
         
         'Card Payment' : 
         r"""^card\ payment\ to       # Trans Type (link word 'to')
         \s(?P<place>.+?)             # Grab where I spent my money
         (,\d+\.\d{2}\s\w{3})?        # How much if available
         (,\ rate\ \d\.\d{0,2}/\w{3})?  # Exchange rate if available 
         [ ,]{0,2}on\s?(?P<date>\d{2,4}[-/]?\w{2,3}[-/]?\d{2,4})?  # Better Date
         (\sn[-a-z ]{0,24})?$          # non-sterling could be cut off""",
    
         'Cash Withdrawal' : 
         r"""^cash\ withdrawal        # Trans Type (link word 'at')
         (\sreversal)?                # could be an ATM error
         \sat\ (?P<place>.+?)         # Where abouts
         (,\d+\.\d{2}\s\w{3})?        # How much if available
         (,\ rate\ \d\.\d{0,2}/\w{3})?  # Exchange rate if available 
         [ ,]{0,3}(on)?
         \s?(?P<date>\d{2,4}[-/]?\w{2,3}[-/]?\d{2,4})?  # Better Date
         (\sn[-a-z ]{0,24})?$          # non-sterling could be cut off""",
   
         'Withdrawal':
         r"""^withdrawal\ .+at
         \s(?P<place>.+)$""",

         'Rejected Bill Payment' : 
         r"""^rejected\ bill\ payment
         \s(via\ faster\ payment\ )?to
         \s(?P<place>.*)$""",
    
         'Bank Giro Credit' :  
         r"""^bank\ giro\ credit\ ref 
         \s(?P<place>.+),\s.*$""",
    
         'Direct Debit' :
         r"""^direct\ debit\ payment
         \sto\s(?P<place>.+?)
         (\sref\ .+?)?
         ,\s?mandate\ no\ \d+$""",
    
         'Faster Payments' :
         r"""^faster\ payments\ receipt
         \s(ref.+)?\ from
         \s(?P<place>.*)$""",
    
         'Standing Order' :  
         r"""standing\ order\ 
         \s(via\ faster\ )?
         payment\ to
         \s(?P<place>.*)
         ,\s?mandate no \d+$""",
    
         'Credit' : 
         r"""^credit\ from 
         \s(?P<place>.*)
         \son
         \s(?P<date>\d{2,4}[-/]\w{3}|\d{2}[-/]\d{2,4})?$""",
         
         'Cheque' : 
         r"""^cheque paid in at (?P<place>.*)$"""}
            
        self.set_trans_type()
        self.extract_data()
   

    @staticmethod
    def parse_statement(path, date_range="all"):
        """This parses the statement, creating santander record objects
        using the information in the statement. It returns a sorted list of 
        record objects. If date_range is all then everything is returned, if
        a tuple of dates (in the form dd-mm-yyyy) is given then records from
        outside this range are not returned"""
        
        field_data_pair = {}
        record_list = []

        with open(path, 'r') as statement:
            # statement is in some ugly format see unit_test.py for examples
            # this script goes some way to convert dos to unix!!
            for record in statement.read().split('\r\n\t\t\t\t\t\t\r\n'):
                
                if len(record.split('\r\n')) == 4:
                    for line in record.split('\r\n'):
                        data = [field.strip('\xa0') for field in line.split(':')]
                        field_data_pair[data[0].lower()] = data[1]
                    
                    condition = True
                    # we expect to have date, amount, balance and description
                    # in all records.
                    for fld in ("date" ,"amount", "balance", "description"):
                        condition &= fld in field_data_pair

                    if not condition:
                        # our statement must be broken
                        msg = "Is the statement broken/currupt\n"
                        msg += "trying to parse:\n{}"
                        raise BadFile(msg.format(record))
                    
                    record_obj = Santander(**field_data_pair)
                    
                    if date_range == "all":
                        # returns everything if date is all
                        record_list.append(record_obj)

                    else:
                        date_format = "%d-%m-%Y"
                        date_min = datetime.datetime.strptime(date_range[0], date_format)
                        date_max = datetime.datetime.strptime(date_range[1], date_format)
                        record_date = record_obj._date
                        
                        if record_date >= date_min and record_date <= date_max:
                            # return only records from within our date range
                            record_list.append(record_obj)
        
        # return a sorted list
        return sorted(record_list, key=lambda x: x.get_date('%s'))
        

    def set_trans_type(self):
        """Sets the transaction type, Also sets the place for easy
        wins"""

        # items here SHOULD NOT go in the transaction regex map
        # This allows us to opt-out of trying to extract data from
        # records that are too easy or just incomplete

        if self._description.startswith("INTEREST"):
            self._trans_type = "Interest"
            self._place = "Santander"
        
        elif self._description == "NON-STERLING PURCHASE FEE":
            self._trans_type = "Bank Charge"
            self._place = "Santander"

        elif self._description.startswith("CASH WITHDRAWAL HANDLING CHARGE"):
            self._trans_type = "ATM fee"
            self._place = "Unknown"
        
        else:
            # once all the badly behaved records are taken into account
            # use the trans regex map for the otheres
            for trans_types in self._trans_regex_map:
                if self._description.startswith(trans_types.upper()):
                    self._trans_type = trans_types
                    break

        if self._trans_type is None:
            # either bug or new transaction type
            msg = "WTF!? Do we have a new transaction type"
            msg += "\ndescription: {}".format(self._description)
            raise RecordError(msg)
            

#### Im not sure im going to implement Natwest transactions ####

class Natwest(Transaction):
    
    account = 'Natwest'
    
    typemap = {'DPC' : 'Bank Giro Credit',
               'POS' : 'Card Payment', 
               'C/L' : 'Cash Withdrawel',
               'D/D' : 'Direct Debit',
               'BAC' : 'Bank Giro Credit',
               'INT' : 'Interest'}
    
    trans_regex_map = \
        {'Cash Withdrawel' : r"'(?P<place>.*?) (?P<date>\d{2}\w{3})",
         'Card Payment' :  r"(?P<date>\d{2}\w{3}\d{2}) , (?P<place>.*?)( , cash back (?P<cashback>\d+.\d+)|$)",  
         'Bank Giro Credit' :  r"'(?P<place>.*?)( , FP (?P<date>[0-3]?[0-9]/[0-1][0-9]/[0-9][0-9])|$)", 
         'Direct Debit' :  r"'(?P<place>.*)",
         'Online Banking' : r"\d{4} , (?P<place>.*?) e FP (?P<date>\d{2}/\d{2}/\d{2})",
         'Interest': r"'(?P<date>\d{2}\w{3}) (?P<place>.*?)$"}

        
    def __init__(self, date, description, amount, balance, transaction_type):
        Transaction.__init__(self, date, description, amount, balance)
        self.transaction_type = self.typemap[transaction_type]
        # FIXME use super

def fromNatwest(path):
    csvfile  = open(path, "rb")
    reader = csv.reader(csvfile)
    column_no = 0
    raw = {}
    objlist = []
    for transaction in reader:
        if transaction == []: continue
        if column_no == 0:
            fieldnames = transaction
        else:
            for index, detail in enumerate(transaction[0:-2]):
                key = fieldnames[index].strip()
                raw.update({key : detail})
        
            foo = Natwest(raw['Date'],
                          raw['Description'],
                          raw['Value'],
                          raw['Balance'],
                          raw['Type'])
        
            foo.extract_data()
            objlist.append(foo)
        
        column_no += 1
            
    csvfile.close()
    return objlist

###### Analysis Starts Here ######


def rolling_totals(list_of_records):
    """Finds the sum of all unique places for a given
    list of record objects"""

    totals = {}
    for record in list_of_records:
        #        if record._place.startswith("TESCO"):

        #    record._place = "TESCO"

        if record._place not in totals:
            totals[record._place] = record.get_amount()

        else:
            totals[record._place] += record.get_amount()


    list_of_places = []
    for place, amount in totals.iteritems():
        list_of_places.append((place, amount))

   
    for place, amount in sorted(list_of_places,key=lambda x: x[1]):
        print "{} --- {}".format(place, amount)


def invout(list_of_records):
    """finds both the total incoming and outgoing"""

    results = {"incoming" : 0, "outgoing" : 0}

    for record in list_of_records:
        amount = record.get_amount()
        if amount > 0:
            results["incoming"] += amount

        else:
            results["outgoing"] -= amount


    msg = "For that period you earnt £{incoming}\n"
    msg += "but you spent £{outgoing}"

    print msg.format(**results)



def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--statement', 
            help='file path to santander text based statement', 
            required=True,
            type=str)
    parser.add_argument('-d', '--date-range',
            default='all',
            help='the date range you want to analyse', 
            type=str,
            nargs=2)

    return parser.parse_args()


def main():
    """main entry point"""

    parser = parse_args()
    file_path = parser.statement
    
    date_range = parser.date_range

    statement = Santander.parse_statement(file_path, date_range)

    rolling_totals(statement)
    print
    invout(statement)
    print
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

















