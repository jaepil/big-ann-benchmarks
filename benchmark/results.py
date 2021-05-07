from __future__ import absolute_import

import h5py
import json
import os
import re
import traceback


def get_result_filename(dataset=None, count=None, definition=None,
                        query_arguments=None):
    d = ['results']
    if dataset:
        d.append(dataset)
    if count:
        d.append(str(count))
    if definition:
        d.append(definition.algorithm)
        data = definition.arguments + query_arguments
        d.append(re.sub(r'\W+', '_', json.dumps(data, sort_keys=True))
                 .strip('_'))
    return os.path.join(*d)


def store_results(dataset, count, definition, query_arguments, attrs, results):
    fn = get_result_filename(
        dataset, count, definition, query_arguments) + '.hdf5'
    head, tail = os.path.split(fn)
    if not os.path.isdir(head):
        os.makedirs(head)
    f = h5py.File(fn, 'w')
    for k, v in attrs.items():
        f.attrs[k] = v
    neighbors = f.create_dataset('neighbors', (len(results), count), 'i')
    for i, idxs in enumerate(results):
        neighbors[i] = idxs
    f.close()


def load_all_results(dataset=None, count=None):
    for root, _, files in os.walk(get_result_filename(dataset, count)):
        for fn in files:
            if os.path.splitext(fn)[-1] != '.hdf5':
                continue
            try:
                f = h5py.File(os.path.join(root, fn), 'r+')
                properties = dict(f.attrs)
                yield properties, f
                f.close()
            except:
                print('Was unable to read', fn)
                traceback.print_exc()


def get_unique_algorithms():
    return set(properties['algo'] for properties, _ in load_all_results())