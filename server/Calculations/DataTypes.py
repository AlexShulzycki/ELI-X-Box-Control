import csv
import os
from enum import Enum

from pydantic import BaseModel, Field


class Element(BaseModel):
    name: str = Field(description="Name of the element", examples=["Copper", "Iron"])
    symbol: str = Field(description="Element symbol", examples=["Cu", "Fe"])
    AbsorptionEnergy: dict[str, float]|None = Field(description="Dict of absorption lines", examples=[{"K": 8979}], default=None)
    EmissionEnergy: dict[str, float]|None = Field(description="Dict of emission lines", examples=[{"Ka1": 8047.78}], default=None)

symbol2name: dict[str, str] = {
    "Ti": "Titanium",
    "V": "Vanadium",
    "Cr": "Chromium",
    "Mn" : "Manganese",
    "Fe" : "Iron",
    "Co" : "Cobalt",
    "Ni": "Nickel",
    "Cu" : "Copper",
    "Zn": "Zinc",
    "Se": "Selenium",
    "Zr": "Zirconium",
    "Nb": "Niobium",
    "Mo": "Molybdenum",
    "Ru": "Rubidium",
    "Pd": "Palladium",
    "Ag": "Silver",
    "Sn": "Tin",
    "Sb": "Antimony",
    "Ta": "Tantalum",
    "Pt": "Platinum",
    "Au":"Gold",
    "Pb": "Lead"
}
"""Self explanatory"""

def loadEnergyCsv(filename):
    """
    Loads in the csv file with elements and corresponding characteristic lines
    Throws an exception if there is an error reading the file

    Does not check whether the file is valid, only tested with "full" csv files without missing columns
    Checking whether the row is partially empty could be a good way to optimize - I am out of time for the moment

    @param filename: name of file from which to read
    @type filename: str
    @return: Dict with elements and characteristic lines, {element:{line:value}}

    """

    data = {}  # Dict to store data from csv

    # Try opening the file
    with open(filename, "r") as f:
        read_file = csv.reader(f, delimiter=',')

        # The first row contains the headers, we will use this to create keys for our dict
        keys = []  # List of columns - Element, Name, Ka1, etc etc

        headers = read_file.__next__()  # Get the headers and move up
        for header in headers:
            keys.append(header)

        # Rest of the file is actual data, process it all!
        for row in read_file:
            # Get the key
            symbol = row[0]
            # Prep the dict
            data[symbol] = {}

            for key in keys[2:-1]:  # Ignore the first two, which is the element and name

                # Add the data to the dict using the correct key
                try:
                    # Hacky way to get key index, can't be bothered to optimize
                    data[symbol][key] = float(row[keys.index(key)])
                except Exception as e:
                    # We have an error
                    if row[keys.index(key)] == '-':
                        # All good, this is by design, we can ignore this part
                        pass
                    else:
                        # We have another problem, raise the exception
                        raise e

        f.close()  # Politely close the file

    return data

elements: dict[str, Element] = {}
"""Loaded in dict of elements {symbol: Element} with their absorption/emission lines from the data folder"""


try:
    # try to load in emission/absorption values
    absorptionEnergy = loadEnergyCsv("data/AbsorptionEnergy.csv")
    emissionEnergy = loadEnergyCsv("data/EmissionEnergy.csv")

    # populate the elements dict, we just loop it twice because I'm lazy

    for symbol, absorption in absorptionEnergy.items():
        if elements.keys().__contains__(symbol):
            elements[symbol].AbsorptionEnergy = absorption
        else:
            # check if we have the name in the dict, otherwise complain to the log
            if not symbol2name.keys().__contains__(symbol):
                name = symbol
                print(f"Element {symbol} does not have a name hardcoded")
            else:
                name = symbol2name[symbol]
            elements[symbol] = Element(
                symbol=symbol,
                name = name,
                AbsorptionEnergy=absorption
            )

    for symbol, emission in emissionEnergy.items():
        if elements.keys().__contains__(symbol):
            elements[symbol].EmissionEnergy = emission
        else:
            # check if we have the name in the dict, otherwise complain to the log
            if not symbol2name.keys().__contains__(symbol):
                name = symbol
                print(f"Element {symbol} does not have a name hardcoded")
            else:
                name = symbol2name[symbol]

            elements[symbol] = Element(
                symbol=symbol,
                name = name,
                EmissionEnergy=emission
            )


except Exception as e:
    print("Error with loading in emission/absorption lines:")
    print(e)





