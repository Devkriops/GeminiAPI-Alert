"""
purpose: script which fetch alerts (deviation from 24-hour average)
based on the current value of pair

Generate an alert if the current price is more than
one standard deviation from the 24hr average
"""

import argparse
import asyncio
from datetime import datetime
import json
from statistics import mean, stdev


# third party
import aiohttp
import requests


async def fetch(session: aiohttp.ClientSession, pair: str, deviation_limit: int) -> dict:
    """
     gathers data for the given currency along the deviation of its value from mean
    :param session:
    :param pair:
    :param deviation_limit:
    :return:
    """
    result = dict(timestamp=None, level='INFO', trading_pair=pair, deviation=None, data={})

    try:
        base_url = "https://api.gemini.com/v2"
        async with session.get(base_url + f"/ticker/{pair}") as response:
            ticker_info = await response.json()
            if response.status != 200:
                raise Exception(ticker_info)

        data = {
            "last_price": None,
            "average": None,
            "change": None,
            "sdev": None
        }

        last_price = float(ticker_info.get('close'))

        closing_prices_of_last_24_hours = list(map(float, ticker_info.get('changes', [])))
        average = mean(closing_prices_of_last_24_hours)

        sample_standard_deviation = stdev(closing_prices_of_last_24_hours, average)

        change = abs(average - last_price)
        sdev = change / sample_standard_deviation

        data.update(last_price=last_price,
                    average=f"{average:.2f}",
                    change=f"{change:0.2f}",
                    sdev=sdev)

        is_deviated = bool(sdev > deviation_limit)

        result.update(timestamp=datetime.now().isoformat(),
                      deviation=is_deviated,
                      data=data)
        return result

    except Exception as ex:
        result.update(timestamp=datetime.now().isoformat(), level="ERROR", message=str(ex))
        return result


async def fetch_all(session: aiohttp.ClientSession, symbols: list, deviation_limit: int) -> tuple:
    """
      gathers the data for each symbol by creating an async task for each symbol
    :param session:
    :param symbols:
    :param deviation_limit:
    :return:
    """
    tasks = []
    for symbol in symbols:
        task = asyncio.create_task(fetch(session, symbol, deviation_limit))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main(pair: str, deviation_limit: int) -> None:
    """
     validates currency and generates the alert
    :param pair:
    :param deviation_limit:
    :return:
    """

    result = {
        "timestamp": None,
        "level": "INFO"
    }

    try:
        # base url to get list of symbols
        base_url = "https://api.gemini.com/v1"
        response = requests.get(base_url + "/symbols")
        symbols = response.json()

        # if response status is other than 200, update the result with error
        if response.status_code != 200:
            result.update(timestamp=datetime.now().isoformat(), level="ERROR", message=symbols)
        else:
            async with aiohttp.ClientSession() as session:
                if pair not in symbols or pair.upper() == "ALL":  # validates currency
                    result = await fetch_all(session, symbols, deviation_limit)
                else:
                    result = await fetch(session, pair, deviation_limit)

    except Exception as ex:
        result.update(timestamp=datetime.now().isoformat(), level="ERROR", message=str(ex))

    finally:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-c", "--currency", help="The currency trading pair, or ALL")

    # Adding optional argument
    parser.add_argument("-d", "--deviation", help="standard deviation threshold. eg. 1")

    # Read arguments from command line
    args = parser.parse_args()

    currency = args.currency if args.currency else 'btcusd'
    deviation = int(args.deviation) if args.deviation and args.deviation.isnumeric() else 1

    asyncio.run(main(currency, deviation))
