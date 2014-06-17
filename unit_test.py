#!/usr/bin/python

"""Unit test for bank statement analyser"""

import unittest2
from money import *
import __builtin__ as builtins
from mock import mock_open, patch


class Test_Everything(unittest2.TestCase):
    """test class"""

    def setup(self):
        pass
    
    def generate_santander_record(self, **kwargs):
        """Generates a santander statement record for 
        test purposes, kwargs are date, description, amount
        and balance. All are stings, this method returns a 
        string that resembles what would be returned from reading
        a santander text statement file object"""
        
        defaults = {"date"        : "07/02/2013",
                    "description" : "BILL PAYMENT VIA FASTER PAYMENT TO Mr Smith  REFERENCE Rent , MANDATE NO 9",
                    "amount"      : "-200.01",
                    "balance"     : "418.67"}
       
        defaults.update(**kwargs)

        test_str = ("Date:\xa0{date}\r\n"
                    "Description:\xa0{description}\r\n"
                    "Amount:\xa0{amount}\xa0\t\r\n"
                    "Balance:\xa0{balance}\xa0")

        return test_str.format(**defaults)

   
        
    def test_date_layouts(self):
        """This testcase looks at the different layouts of the
        date and makes sure all sensible cases are handles"""

        test_string = ("From:\xa001/11/2012\xa0to\xa005/11/2013\r\n\t\t\t\t\t\t\t\r\n"
                       "Account:\xa0XXXX XXXX XXXX XXXX\r\n\t\t\t\t\t\t\r\n")

        tcases = ("01/11/2012", "01/11/12", "01-11-2012", "2012-11-01")

        for tcase in tcases:
            description = "CARD PAYMENT TO SAINSBURY'S S/MKT,16.10 GBP, RATE 1.00/GBP ON {}"
            test_string += self.generate_santander_record(description=description.format(tcase)) + '\r\n\t\t\t\t\t\t\r\n'
        
        test_string += self.generate_santander_record(description=description.format("01NOV12"))

        with patch.object(builtins, 'open', mock_open(read_data=test_string)):
            statement = Santander.parse_statement('ignore')

        for record in statement:
            #    print record.description
            self.assertEqual(record.date.strftime('%d/%m/%Y'), "01/11/2012")


    def test_bill_payment_variations(self):
        """Tests all variations of bill payment description"""

        test_string = ("From:\xa001/11/2012\xa0to\xa005/11/2013\r\n\t\t\t\t\t\t\t\r\n"
                       "Account:\xa0XXXX XXXX XXXX XXXX\r\n\t\t\t\t\t\t\r\n")
        
        tcases = ("BILL PAYMENT VIA FASTER PAYMENT TO MISS CM SMITH REFERENCE IOU , MANDATE NO 7",
                 "BILL PAYMENT VIA FASTER PAYMENT TO MISS CM SMITH REFERENCE IOU, MANDATE NO 7",
                 "BILL PAYMENT TO MISS CM SMITH REFERENCE IOU , MANDATE NO 7",
                 "BILL PAYMENT TO MISS CM SMITH REFERENCE IOU ,MANDATE NO 7",
                 "BILL PAYMENT TO MISS CM SMITH ,MANDATE NO 7",
                 "BILL PAYMENT TO MISS CM SMITH, MANDATE NO 7",
                 "BILL PAYMENT TO MISS CM SMITH REFERENCE IOU",
                 "BILL PAYMENT TO MISS CM SMITH")

        # change index (tcases[n:-1]) to isolate strings to test
        for tcase in tcases[ :-1]:
            test_string += self.generate_santander_record(description=tcase) + '\r\n\t\t\t\t\t\t\r\n'
        test_string += self.generate_santander_record(description=tcases[-1])

        with patch.object(builtins, 'open', mock_open(read_data=test_string)):
            statement = Santander.parse_statement('ignore')
        
        for record in statement:
            msg = "\nDescription:\n{}\nRegex:\n{}\n"
            self.assertEqual(record._place, "MISS CM SMITH",
                             msg.format(record.description,
                                        record.trans_regex_map[record.transaction_type]))
        

    def test_card_payment_variations(self):
        """Tests all variations of card payment descriptions"""

        test_string = ("From:\xa001/11/2012\xa0to\xa005/11/2013\r\n\t\t\t\t\t\t\t\r\n"
                       "Account:\xa0XXXX XXXX XXXX XXXX\r\n\t\t\t\t\t\t\r\n")

        tcases = ("CARD PAYMENT TO PETS AT HOME LTD,15.50 GBP, RATE 1.00/GBP ON 23-11-2014",
                  "CARD PAYMENT TO PETS AT HOME LTD, ON 23-11-2014",
                  "CARD PAYMENT TO PETS AT HOME LTD,15.50 GBP ON 23-11-2014",
                  "CARD PAYMENT TO PETS AT HOME LTD,15.50 GBP ON", 
                  "CARD PAYMENT TO PETS AT HOME LTD,15.50 USD, RATE 0.60/GBP ON 23-11-2014 NON-STERLING",
                  "CARD PAYMENT TO PETS AT HOME LTD,15.50 USD, RATE 0.60/GBP ON 23-11-2014 NON-STERLI")

        
        # change index (tcases[n:-1]) to isolate strings to test
        for tcase in tcases[:-1]:
            test_string += self.generate_santander_record(description=tcase) + '\r\n\t\t\t\t\t\t\r\n'
   
        test_string += self.generate_santander_record(description=tcases[-1])

        with patch.object(builtins, 'open', mock_open(read_data=test_string)):
            statement = Santander.parse_statement('ignore')

        for record in statement:
            msg = "\nDescription:\n{}\nRegex:\n{}\n"
            self.assertEqual(record._place, "PETS AT HOME LTD",
                             msg.format(record.description,
                                        record.trans_regex_map[record.transaction_type]))


    def test_cash_withdrawal(self):
        """Tests all variations of cash withdrawal descriptions"""

        test_string = ("From:\xa001/11/2012\xa0to\xa005/11/2013\r\n\t\t\t\t\t\t\t\r\n"
                       "Account:\xa0XXXX XXXX XXXX XXXX\r\n\t\t\t\t\t\t\r\n")


        place = "TESCO PERSONAL FINANCE ATM TESCO MILTON, MILTON, CAMBRID"
        
        tcases = ("CASH WITHDRAWAL AT " + place + ",30.00 GBP , ON",
                  "CASH WITHDRAWAL AT " + place + ",30.00 GBP , ON 09-08-2014",
                  "CASH WITHDRAWAL REVERSAL AT " + place,
                  "CASH WITHDRAWAL AT " + place + ",30.00 USD, RATE 0.60/GBP ON 09-08-2014 NON")
        
        for tcase in tcases[:-1]:
            test_string += self.generate_santander_record(description=tcase) 
            test_string += '\r\n\t\t\t\t\t\t\r\n'
 
        test_string += self.generate_santander_record(description=tcases[-1])

        with patch.object(builtins, 'open', mock_open(read_data=test_string)):
            statement = Santander.parse_statement('ignore')

        for record in statement:
            msg = "\nDescription:\n{}\nRegex:\n{}\n"
            self.assertEqual(record._place, place,
                             msg.format(record.description,
                                        record.trans_regex_map[record.transaction_type]))


    def test_bank_giro_credit(self):
        """Tests bank gira credit descriptions"""

        test_string = ("From:\xa001/11/2012\xa0to\xa005/11/2013\r\n\t\t\t\t\t\t\t\r\n"
                       "Account:\xa0XXXX XXXX XXXX XXXX\r\n\t\t\t\t\t\t\r\n")


        tcase = "BANK GIRO CREDIT REF YOUR MOTHER, 483834dfg"
        test_string += self.generate_santander_record(description=tcase) 
 
        with patch.object(builtins, 'open', mock_open(read_data=test_string)):
            statement = Santander.parse_statement('ignore')
        
        for record in statement:
            msg = "\nDescription:\n{}\nRegex:\n{}\n"
            print record._place
            self.assertEqual(statement[0]._place, "YOUR MOTHER",
                             msg.format(record.description,
                                        record.trans_regex_map[record.transaction_type]))


if __name__ == '__main__':
    unittest2.main()

# testcases = (
# "A Random String",
# 
# """From: 20/11/2012 to 06/02/2013
# 
# Account: XXXX XXXX XXXX XXXX
# 
# Date: 07/02/2013
# Description: BILL PAYMENT VIA FASTER PAYMENT TO Mr RM Smith REFERENCE Rent , MANDATE NO 9
# Amount: -200.00
# Balance: 418.67
# 
# Date: 06/02/2013
# Description: CASH WITHDRAWAL AT TESCO PERSONAL FINANCE ATM TESCO MILTON, MILTON, CAMBRID,10.00 GBP , ON
# Amount: -10.00
# Balance: 618.67
# 
# Date: 06/02/2013
# Description: CARD PAYMENT TO TESCO UPT 3896,40.16 GBP, RATE 1.00/GBP ON 04-02-2013
# Amount: -40.16
# Balance: 628.67
# 
# Date: 06/02/2013
# Description: CARD PAYMENT TO TESCO STORES-2889,12.00 GBP, RATE 1.00/GBP ON 04-02-2013
# Amount: -12.00
# Balance: 668.83
# """,
# 
# """From: 20/11/2012 to 06/02/2013
# 
# Account: XXXX XXXX XXXX XXXX
# 
# Date: 07/02/2013
# Description: BILL PAYMENT VIA FASTER PAYMENT TO Mr RM Smith REFERENCE Rent , MANDATE NO 9
# Amount: -200.00
# Balance: 418.67
# 
# Date: 06/02/2013
# Description: CASH WITHDRAWAL AT TESCO PERSONAL FINANCE ATM TESCO MILTON, MILTON, CAMBRID,10.00 GBP , ON
# Amount: -10.00
# Balance: 618.67
# 
# Date: 07/02/2013
# Description: BILL PAYMENT VIA FASTER PAYMENT TO Mr RM Smith REFERENCE Rent , MANDATE NO 9
# Amount: -200.00
# Balance: 418.67
# 
# Date: 06/02/2013
# Description: CARD PAYMENT TO TESCO STORES-2889,12.00 GBP, RATE 1.00/GBP ON 04-02-2013
# Amount: -12.00
# Balance: 668.83
# """)
