Purpose
----------
Generate an alert if the current price is more than one standard deviation from the 24hr average

Dependencies
--------------
    $ python --version 3.8.10
    $ pip install virtualenv

Linux
----------
    $ virtualenv .venv
    $ source .venv/bin/activate

    $ pip install aiohttp requests pylint

Windows
-----------
    $ virtualenv .venv
    $ .venv\Scripts\activate

    $ pip install aiohttp requests pylint


Usuage
------------------

python api_alerts.py -c btcusd -d 1

python api_alerts.py -c all -d 1

python api_alerts.py -c ALL -d 2

python api_alerts.py

api_alerts

Next steps and Other interesting checks 
-----------------------------------------

We can implement pub sub model by monitoring the values and make this script as a publisher for different events

Approach
-----------------

1. using requests library fetched the ticker data for btcusd from https://api.gemini.com/v2/ticker/btcusd
2. calculated average, standard deviation, price deviation from the fields close, changes in json response using statistics library
3. printed the result
4. Improved by taking pair and deviation_limit as arguments to the function to make it more dynamic
5. Improved by taking pair and deviation_limit from command line args using argparse library
6. Validated the input currency by using response of symbols endpoint https://api.gemini.com/v1/symbols
7. If currency is ALL, we have to fetch the data of each symbol from ticker endpoint. 
8. Synchronous programming is taking time to fetch data of each symbol. So, improved it by adding async tasks for each symbol using asyncio and aiohttp libraries
9. Documentation

Time
--------------------
1 and half hour to understand
30 mins for design
1 hour for implementation
30 mins for improvement
30 mins for documentation


