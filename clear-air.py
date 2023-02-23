import logging

import numpy as np
import pandas as pd


def genLogger(name: str, rank: int,
              level: int = logging.DEBUG, formatting: str = ''):
    if (name == ''):
        raise Exception('invalid logger name')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    tab = rank * '\t'
    formatting = f'{tab}%(levelname)s >> %(message)s'
    formatter = logging.Formatter(formatting, datefmt='%H:%M')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":

    # Initialize logging
    logging.basicConfig(filename='processing.log',
                        filemode='w',
                        level=logging.DEBUG)
    logger = genLogger('0', 0)
