# Bank Statement Analyser

This is a simple bank statement analyser app written in python. This is a personal learning exercise which aims to use lots of standard library calls and hopefully teach me regular expressions. 

I really wanted to do some sort of data analysis project but couldnt think of interesting and easily parsable data sets. Seeing as im the kind of person who always pays for stuff using debit cards, I realised that there may be a wealth of information I can learn about myself from my bank statements. Think about it, every time you go out there is a record of where you had lunch, what you did and maybe even how you got there. What about how much you spend on food per week? Is it efficient or are you just buying expensive crap that is making you fat? How long do these records go back? Maybe I could detect food prices changing with inflation and market variations.


Im always looking to improve to any comments will be greatly appreciated.

The design is simple:

 * First write a parser (using regex to learn how they work)
 * Create a database of places where I spend my money and try and work out what I most likely spent my money on.
 * Create a database of transactions (maybe use sqlite as its easy)
