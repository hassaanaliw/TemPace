import csv
import operator
from datetime import datetime
from collections import deque
import pprint

import numpy
import numpy as np
import pandas as pd
from dateutil.parser import parse


def get_chain_readings(csv_data):
    count = 0
    big_container = []
    actual = []
    chain = []
    prev = 0

    df = pd.read_csv(csv_data,
                     names=['sourceName', 'sourceVersion', 'device', 'type', 'unit', 'creationDate',
                            'startDate', 'endDate', 'value'])
    items = (df.tail(5000))
    items = items.iloc[1:]

    for (i, x) in enumerate(items.values):

        startdate = parse(x[6])
        enddate = parse(x[7])
        distance = x[8]
        if not chain:
            # small chain has now started
            chain.append(
                {
                    'start': startdate,
                    'end': enddate,
                    'distance': distance
                }
            )
            prev = enddate
        elif chain:
            if startdate == prev:
                # continue the chain
                chain.append(
                    {
                        'start': startdate,
                        'end': enddate,
                        'distance': distance
                    }
                )
                prev = enddate
            else:
                # You said you would never break the chain
                big_container.append(chain)
                chain = []
                chain.append(
                    {
                        'start': startdate,
                        'end': enddate,
                        'distance': distance
                    }
                )
                prev = enddate

    for row in big_container:
        sums = 0
        if len(row) <= 2:
            big_container.remove(row)
        elif len(row) > 2:
            for r in row:
                sums += (float(r["distance"]))

            if (float(sums) / len(row)) > 0.4:
                print(float(sums) / len(row))
                actual.append(row)

    print(len(actual))
    return actual


