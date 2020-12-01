from src.dirs import DATAHOME, regions
from src.io import load_csvs
import pandas as pd

from shutil import rmtree

region = 'NSW1'
sample = 'demand_2015-01_clean.csv'

raw = load_csvs('raw', recursive=True, match='clean', verbose=True)
raw = {k.split('/')[-1]: v for k, v in raw.items()}

cols = [
    'SETTLEMENTDATE',
    'TOTALDEMAND',
    'REGIONID',
    'TOTALINTERMITTENTGENERATION',
    'DEMANDFORECAST',
    'INTERVENTION'
]

out = DATAHOME / 'processed' / 'demand'
rmtree(out, ignore_errors=True)
out.mkdir(exist_ok=True)

for name, all_regions in raw.items():
    all_regions = all_regions.loc[:, cols]
    all_regions.loc[:, 'SETTLEMENTDATE'] = pd.to_datetime(all_regions.loc[:, 'SETTLEMENTDATE'])
    regions = list(set(all_regions.loc[:, 'REGIONID']))

    for region in regions:
        print(f'processing {name}, {region}')
        mask = all_regions.loc[:, 'REGIONID'] == region
        data = all_regions.loc[mask, :]
        data = data.set_index('SETTLEMENTDATE').sort_index()

        dupes = data.index.duplicated(keep='last')
        data = data.loc[~dupes, :]

        #  check datetime index integrity
        index_check = pd.date_range(start=data.index[0], end=data.index[-1], freq='5min')
        assert index_check.shape[0] == data.shape[0]
        assert all(index_check == data.index)

        region_folder = out / region
        region_folder.mkdir(exist_ok=True)

        data.to_csv(
            (region_folder / name.split('_')[1]).with_suffix('.csv')
        )

        concat = region_folder / 'all.csv'
        data.to_csv(
             concat, mode='a', header=not concat.is_file()
        )


def make_all():
    data = pd.concat([pd.read_csv(DATAHOME / 'processed' / 'demand' / r / 'all.csv') for r in regions], axis=0)
    assert set(data['REGIONID']) == set(regions)
    out_dir = DATAHOME / 'processed' / 'demand' / 'all'
    out_dir.mkdir(exist_ok=True)
    data.to_csv(out_dir / 'all.csv')

#make_all()
