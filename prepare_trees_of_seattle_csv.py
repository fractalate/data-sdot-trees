import os
import json

import pandas as pd

from sdot import SDOT
from wcvp import WCVP

print('Loading datasets...')

sdot = SDOT('SDOT_Trees_CDL_20241119.csv')
wcvp = WCVP('wcvp_taxon.csv', 'wcvp_distribution.csv')

pairs = [
    ('Acer truncatum x A platanoides', 'Acer truncatum var. platanoides'),
]

scientificnames, scientificnames_clean = zip(*pairs)
alternative_scientific_names = pd.DataFrame({
    'scientificname': scientificnames,
    'scientificname_clean': scientificnames_clean,
})
print(alternative_scientific_names)
import sys
sys.exit(0)

df = pd.DataFrame()
df['scientificname'] = sdot.dfsdot['SCIENTIFIC_NAME']
wcvp.assert_all_scientificnames_values_have_one_establishment_means_in_locality(df, 'Washington')

'''
# This one will fail!
df = pd.DataFrame({ 'scientificname': ['Artemisia violacea'] })
wcvp.assert_all_scientificnames_values_have_one_establishmentmeans_in_locality(df, 'Washington')
'''

print('Checks passed!')

'''
plants = [
    'Artemisia campestris subsp. borealis',
    'Artemisia vulgaris subsp. vulgaris',
    'Cercis canadensis',
    'Stump',
]

for plant in plants:
    print(plant, '-', wcvp.lookup_establishment_type('Washington', plant))
'''

dftaxon = wcvp.get_dftaxon_for_locality('Washington')
dftaxon['indigenous'] = dftaxon.apply(lambda x: x['locality'] == 'Washington' and x['establishmentmeans'] != 'introduced', axis=1)

trees = pd.merge(
    sdot.dfsdot[['OBJECTID', 'SCIENTIFIC_NAME', 'GENUS', 'x', 'y']],
    dftaxon[['scientificname', 'locality', 'indigenous']],
    left_on='SCIENTIFIC_NAME',
    right_on='scientificname',
    how='left',
)
trees['indigenous'].infer_objects(copy=False)
trees['indigenous'] = trees.apply(lambda x: x['indigenous'] == True, axis=1)  # Fill NaN with False. There's got to be a way to do this.
trees['local'] = trees['locality'] == 'Washington'
trees['scientificname'] = trees['SCIENTIFIC_NAME']
trees['genus'] = trees['GENUS']
trees['objectid'] = trees['OBJECTID']
trees = trees[['objectid', 'scientificname', 'genus', 'local', 'indigenous', 'x', 'y']]

os.makedirs('data', exist_ok=True)

trees_csv = 'data/trees_of_seattle.csv'
trees.to_csv(trees_csv, sep = '|', index=False)
print(f'Saved {len(trees)} records to {trees_csv}')
trees_csv_metadata_json = 'data/trees_of_seattle.csv.metadata.json'
with open(trees_csv_metadata_json, 'w') as fout:
    fout.write(json.dumps({
        'version': '1',
        'record_count': len(trees),
    }, indent='  ') + '\n')
print(f'Metadata saved to {trees_csv_metadata_json}')
