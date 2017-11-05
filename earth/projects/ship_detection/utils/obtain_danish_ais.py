import time

from io import StringIO
from sqlalchemy import create_engine
import subprocess as sp
from multiprocessing import Process
import os

import pandas as pd
import numpy as np


def get_process_image(i):
    print('working on ftp://ftp.ais.dk/ais_data/aisdk_{}.csv...'.format(i))

    print(sp.call('wget ftp://ftp.ais.dk/ais_data/aisdk_{}.csv'.format(i), shell=True, stderr=open(os.devnull, 'wb')))
    with open('aisdk_{}.csv'.format(i), 'r') as f:
        df = pd.read_csv(f)
    print('downloaded aisdk_{}.csv'.format(i))

    del df['Cargo type']
    del df['Destination']
    del df['ETA']

    df.columns = [
        'timestamp',
        'vessel_type',
        'mmsi',
        'latitude',
        'longitude',
        'navigational_status',
        'rate_of_turn',
        'speed_over_ground',
        'course_over_ground',
        'heading',
        'imo',
        'callsign',
        'name',
        'ship_type',
        'width',
        'length',
        'position_fixing_method',
        'draught',
        'data_source'
    ]

    df['timestamp'] = df['timestamp'].map(lambda x: '{}-{}-{} {}'.format(x[6:10], x[3:5], x[:2], x[11:]))
    df.replace('Unknown', np.NaN, inplace=True)
    df.replace('Undefined', np.NaN, inplace=True)
    df.replace('Unknown value', np.NaN, inplace=True)
    df.replace('Unk', np.NaN, inplace=True)
    print('processed aisdk_{}.csv'.format(i))

    conn = create_engine("mysql://{}@{}/{}".format(
        'root', '104.199.118.158', 'earthdat'
    ))
    for j in range(int(df.shape[0] / 500000) + 1)[:5]:
        df[500000*j:500000*(j+1)].to_sql('denmark_ais', conn, if_exists='append', index=False)
        print('uploaded iteration {}/{} for aisdk_{}.csv'.format(j + 1, int(df.shape[0] / 500000) + 1, i))

processes = []
for i in range(20171001, 20171030):
    if len(processes) > 4:
        for p in processes: p.join()

    p = Process(target=get_process_image, args=(i,))
    processes.append(p)
    p.start()
    time.sleep(1)
