from pathlib import Path
import numpy as np
import pandas as pd
import json
from src.dirs import DATAHOME, regions
from src.io import load_csvs


def baseline_season(demand, day_len, season_len):
    demand = demand.reshape(-1, day_len)
    pred = demand[:-season_len, :]
    target = demand[season_len:, :]
    return pred, target


def run_baseline(name, data, day_len=288, season_len=1):
    data = data.set_index('SETTLEMENTDATE')
    data = data.sort_index()
    pred, target = baseline_season(
        data.loc[:, 'TOTALDEMAND'].values,
        day_len=day_len,
        season_len=season_len
    )
    pred_index, target_index = baseline_season(data.index.values, day_len=day_len, season_len=season_len)

    pred_index = pd.DataFrame(pred_index)
    target_index = pd.DataFrame(target_index)
    error_fi = DATAHOME / 'final' / 'baselines' / name / 'errors.jsonl'
    error_fi.unlink(missing_ok=True)

    stats = []
    for idx, day in enumerate(pred_index.iloc[:, 0]):
        data = pd.DataFrame({
            'pred': pred[idx, :],
            'target': target[idx, :],
            'pred_index': pd.to_datetime(pred_index.iloc[idx, :]),
            'target_index': pd.to_datetime(target_index.iloc[idx, :]),
            'errors': pred[idx, :] - target[idx, :],
            'abs-errors': abs(pred[idx, :] - target[idx, :])
        })
        day = day.split(' ')[0]
        path = DATAHOME / 'final' / 'baselines' / name / region
        path.mkdir(exist_ok=True, parents=True)
        path = (path / day).with_suffix('.csv')
        data.to_csv(path)
        desc = data.describe()
        desc.index.name = 'statistic'
        desc = desc.loc[['mean', 'min', 'max'], :]
        desc = desc.reset_index().melt('statistic')
        desc.loc[:, 'target_day'] = data.iloc[0, :].loc['target_index']
        stats.append(desc)

    stats = pd.concat(stats, axis=0)
    stats.to_csv(DATAHOME / 'final' / 'baselines' / name / 'errors.csv', index=False)


if __name__ == '__main__':
    raw = load_csvs('processed', recursive=True, match='all', verbose=True)
    raw = {k.split('/')[-2]: v for k, v in raw.items()}
    print(raw.keys())

    region = 'SA1'
    data = raw[region]
    run_baseline('yesterday', data, 288, 1)
    run_baseline('week', data, 288, 7)
