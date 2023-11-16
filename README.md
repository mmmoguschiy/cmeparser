This script reads data from the daily CMEGroup settlement report, laid out in JSON format. The script is adapted for the Eurodollar tool. The result is displayed on the screen.

To run, enter the command:

python cmeparser.py M 05/25/2021

Where:

M - the letter of the expiration month (in this case, it is June)

05 - month
25 - number
2021 - year

The month, day and year form the date on which the report is available.


Branches

plot - Output of an open interest diagram

maxpain - calculation and output of the maxpain diagram
