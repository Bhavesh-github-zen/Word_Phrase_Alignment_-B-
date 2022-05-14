#!/usr/bin/env python
# -*- coding: utf8 -*-

'''
Script that selects train, dev and test sets for DRSs for a certain language

Dev/test splits:
English: dev part X1, test part X0, rest train
German: dev X0, X1, test X2, X3, rest train
Dutch/Italian: dev part X1, X3, X5, X7 and X9, test part X0, X2, X4, X6 and X8, no training set
'''

import argparse
import os
import re
import random


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", '--release_root', required=True, type=str, help="Root of release files")
    parser.add_argument("-o", '--output_folder', required=True, type=str, help="Folder to write output DRSs to (file-names are standardized)")
    parser.add_argument("-l", '--language', default='en', choices=['en', 'de', 'nl', 'it'], type=str, help="Languages we select")
    parser.add_argument("-d", '--data_type', choices=['gold', 'silver', 'bronze'], help="Whether we extract gold/silver/bronze data")
    parser.add_argument("-rs", '--random_seed', default=32, type=int, help="Random seed for shuffling of the data -- use our default 32 to get our version")
    args = parser.parse_args()
    return args


def shuffle_dependent_lists(lst1, lst2, seed):
    '''Shuffle lists but keep dependency between the two'''
    assert len(lst1) == len(lst2)

    num_list = [i for i in range(len(lst1))]
    random.Random(seed).shuffle(num_list)
    new_lst1, new_lst2 = [], []
    # Add items based on random list of numbers
    for idx in num_list:
        new_lst1.append(lst1[idx])
        new_lst2.append(lst2[idx])
    return new_lst1, new_lst2


def write_to_file(lst, out_file):
    '''Write list to file'''
    with open(out_file, "w") as out_f:
        for line in lst:
            out_f.write(line.strip() + '\n')
    out_f.close()


def write_list_of_lists(lst, out_file, extra_new_line=True):
    '''Write lists of lists to file'''
    with open(out_file, "w") as out_f:
        for sub_list in lst:
            for item in sub_list:
                out_f.write(item.strip() + '\n')
            if extra_new_line:
                out_f.write('\n')
    out_f.close()


def create_output(raw, drss, out_file, seed):
    '''Create output given lists'''
    assert len(raw) == len(drss), "Raw and DRSs are not equal length: {0} vs {1}".format(len(raw), len(drss))
    if len(raw) > 0 and len(drss) > 0:
        # Randomize lists but keep dependency
        all_lines, sents = shuffle_dependent_lists(drss, raw, seed)
        # Always write all DRSs to file
        write_list_of_lists(all_lines, out_file)
        write_to_file(sents, out_file + '.raw')


def get_files(root_dir, lang):
    '''Get all the files we need from the root directory'''
    res_list = []
    for root, dirs, files in os.walk(root_dir):
        if files:
            cur_path = os.path.dirname(os.path.join(root, files[0])) + '/'
            raw_file = '{0}{1}.raw'.format(cur_path, lang)
            drs_file = '{0}{1}.drs.clf'.format(cur_path, lang)
            if os.path.isfile(raw_file) and os.path.isfile(drs_file):
                part = re.findall(r'p(\d\d)/', cur_path)[0]
                doc = re.findall(r'd(\d\d\d\d)/', cur_path)[0]
                raw = " ".join([x.strip() for x in open(raw_file, 'r') if x.strip()])
                drs = [x.strip() for x in open(drs_file, 'r') if x.strip()]
                res_list.append([part, doc, raw, drs])
    return res_list


def get_train_dev_test_parts(lang, data_type):
    '''Function that returns a list of parts that are in dev and test,
       to make sure that those are not included in training
       We have a different split for the languages
       because for Dutch/Italian we currently only have dev/test'''
    # First set all possible parts
    possible_parts = ['0' + final_num if len(final_num) < 2 else final_num for final_num in [str(num) for num in range(0, 100)]]

    # Silver/Bronze does not have dev/test
    if data_type != 'gold':
        return possible_parts, [], []

    # Now for each language return their respective split
    if lang == 'en':
        # English: dev part X1, test part X0, rest train
        train_parts = [p for p in possible_parts if p[-1] not in ['0', '1']]
        dev_parts = [p for p in possible_parts if p[-1] == '0']
        test_parts = [p for p in possible_parts if p[-1] == '1']
    elif lang == 'de':
        # German: dev X0, X1, test X2, X3, rest train
        train_parts = [p for p in possible_parts if p[-1] not in ['0', '1', '2', '3']]
        dev_parts = [p for p in possible_parts if p[-1] in ['0', '1']]
        test_parts = [p for p in possible_parts if p[-1] in ['2', '3']]
    elif lang in ['it', 'nl']:
        # Dutch/Italian: dev part X1, X3, X5, X7 and X9, test part X0, X2, X4, X6 and X8, no training set
        train_parts = []
        dev_parts = [p for p in possible_parts if p[-1] in ['1', '3', '5', '7', '9']]
        test_parts = [p for p in possible_parts if p[-1] in ['0', '2', '4', '6', '8']]
    else:
        raise ValueError("Language {0} not implemented".format(lang))
    # Finally return the parts
    return train_parts, dev_parts, test_parts


if __name__ == "__main__":
    args = create_arg_parser()

    # Get parts that are only in dev/test
    train_parts, dev_parts, test_parts = get_train_dev_test_parts(args.language, args.data_type)

    # Set filenames
    train_file = '{0}train.txt'.format(args.output_folder)
    dev_file = '{0}dev.txt'.format(args.output_folder)
    test_file = '{0}test.txt'.format(args.output_folder)

    # Read all DRSs and sentences from the release files
    res_list = get_files(args.release_root, args.language)

    # Split train/dev/test based on dev_parts and test_parts
    training_items = [x for x in res_list if x[0] in train_parts]
    dev_items = [x for x in res_list if x[0] in dev_parts]
    test_items = [x for x in res_list if x[0] in test_parts]

    # Finally create the output files
    print ('\nLengths of train/dev/test: {0}/{1}/{2}\n'.format(len(training_items), len(dev_items), len(test_items)))
    if training_items:
        create_output([x[2] for x in training_items], [x[3] for x in training_items], train_file, args.random_seed)
    if dev_items:
        create_output([x[2] for x in dev_items], [x[3] for x in dev_items], dev_file, args.random_seed)
    if test_items:
        create_output([x[2] for x in test_items], [x[3] for x in test_items], test_file, args.random_seed)

