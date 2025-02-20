import pandas as pd
import image_classifier as clf
import time
from openpyxl import load_workbook

def parse_feature_selection(row):
    fsel = []
    if row.hog_weight > 0:
        fsel.append('hog')
    if row.circles_weight > 0:
        fsel.append('circles')
    if row.hist_weight > 0:
        fsel.append('hist')
    return fsel

def parse_red_params(row):
    lr1 = [int(item) for item in row.low_r1.split(', ')]
    lr2 = [int(item) for item in row.low_r2.split(', ')]
    ur1 = [int(item) for item in row.up_r1.split(', ')]
    ur2 = [int(item) for item in row.up_r2.split(', ')]
    return {'lr1': lr1, 'lr2': lr2, 'ur1': ur1, 'ur2': ur2}

def parse_circle_params(row):
    circles = {}
    circles['kernel_size'] = [int(item) for item in row.kernel_size.split(', ')]
    circles['stdx'] = row.stdx
    circles['dp'] = row.dp
    circles['minDist'] = row.minDist
    circles['param1'] = row.param1
    circles['param2'] = row.param2
    circles['minRadius'] = row.minRadius
    circles['maxRadius'] = row.maxRadius
    return circles

def parse_hist_params(row):
    hist = {}
    hist['bins'] = row.bins
    hist['channels'] = [int(item) for item in row.channels.split(', ')]
    hist['ranges'] = [int(item) for item in row.ranges.split(', ')]
    return hist

def parse_hog_params(row):
    hog = {}
    hog['ornts'] = row.ornts
    hog['ppc'] = [int(item) for item in row.ppc.split(', ')]
    hog['cpb'] = [int(item) for item in row.cpb.split(', ')]
    return hog


def parse_parameters(row):
    params = {}
    params['train_path'] = row.train_path
    params['test_path'] = row.test_path
    params['n'] = row.n
    params['weight'] = {'hog': row.hog_weight, 'circles': row.circles_weight, 'hist': row.hist_weight}
    params['fsel'] = parse_feature_selection(row)
    params['hog'] = parse_hog_params(row)
    params['red'] = parse_red_params(row)
    params['circles'] = parse_circle_params(row)
    params['hist'] = parse_hist_params(row)
    return params


def update_df_row(stats, row, df):
    df.at[row.Index, "total_deathstar"] = stats['ds']['total']
    df.at[row.Index, "accurate_deathstar"] = stats['ds']['accurate']
    df.at[row.Index, "inaccurate_deathstar"] = stats['ds']['inaccurate']

    df.at[row.Index, "total_non-deathstar"] = stats['nds']['total']
    df.at[row.Index, "accurate_non-deathstar"] = stats['nds']['accurate']
    df.at[row.Index, "inaccurate_non-deathstar"] = stats['nds']['inaccurate']

    total_images = stats['nds']['total'] + stats['ds']['total']
    ds_accurate = round(stats['ds']['accurate'] / stats['ds']['total'] * 100, 2)
    nds_accurate = round(stats['nds']['accurate'] / stats['nds']['total'] * 100, 2)
    total_accurate = (stats['ds']['accurate'] + stats['nds']['accurate']) / total_images
    total_accurate = round(total_accurate * 100, 2)

    df.at[row.Index, "ds_accuracy"] = ds_accurate
    df.at[row.Index, "nds_accuracy"] = nds_accurate
    df.at[row.Index, "total_accuracy"] = total_accurate
    df.at[row.Index, "elapsed_time"] = stats['time']

    return df


# inclusive
id_range = {'low': 80, 'high': 80}

# Read the .xlsx file
file_path = '..//data/parameter_list.xlsx'
df = pd.read_excel(file_path)

print(df)

df = df[(df['ID'] >= id_range['low']) & (df['ID'] <= id_range['high'])]
for row in df.itertuples():
    print(f"Starting row ID #{row.ID}/{id_range['high']}")
    start = time.time()
    params = parse_parameters(row)
    features = clf.extract_features(params)
    kNN = clf.train_model(features['data'], features['labels'], params)
    stats = clf.test_model(kNN, params)
    stats['time'] = round(time.time() - start, 2)
    df = update_df_row(stats, row, df)
    clf.print_accuracy(stats['ds'], stats['nds'])
    print(f"Total time: {stats['time']} seconds")
    print(f"Finished row {row.ID}\n")


# Write back the modified DataFrame
print("Completed number crunching, writing to excel file now...")
with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
    df.to_excel(writer, index=False)

print("Done writing to excel file")