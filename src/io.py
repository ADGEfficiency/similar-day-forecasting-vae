from pathlib import Path
import json

import pandas as pd

from src.dirs import HOME


def load_csvs(folder='raw', recursive=False, match='', verbose=False):
    """loads all CSVs in a directory"""
    base = Path(HOME, 'data', folder)

    if recursive:
        pattern = '**/*.csv'
    else:
        pattern = '*.csv'

    data = {}
    fpaths = [fpath for fpath in base.glob(pattern) if match in fpath.name]
    for fpath in fpaths:
        if verbose:
            print(f'loading {fpath}')
        #  in case we hit CSVs pandas can't parse, ignore ParserError
        try:
            df = pd.read_csv(fpath, low_memory=False)
            #  drop an index col if we load one by accident
            df.drop("Unnamed: 0", axis=1, inplace=True, errors='ignore')
            data[str(fpath.relative_to(base))] = df
        except pd.errors.ParserError:
            pass
    return data


def load_jsonls(base, recursive=False):
    """loads all JSON Lines files in a directory"""
    if recursive:
        pattern = '**/*.jsonl'
    else:
        pattern = '*.jsonl'
    dataset = []
    print(base)
    for fpath in base.glob(pattern):
        with open(fpath, 'r') as fi:
            for line in fi.readlines():
                data = json.loads(line)
                dataset.append(data)
    return dataset
