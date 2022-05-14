#!/bin/bash
set -eu -o pipefail

# Script that creates/extracts/setups all train/dev/test data sets for all languages
# We assume you run this script from the main release folder, so these folders should exist:
#   data/en/gold/
#   data/en/silver/
#   data/en/bronze/
#   data/de/gold/
#   ....
#   etc

echo "Extracting train/dev/test sets"
echo "Note that this might take a few hours"
echo "To save time, it's recommended to download the files directly: https://pmb.let.rug.nl/releases/exp_data_4.0.0.zip"
echo '---'
echo "We assume that ''python'' calls Python 3 in your environment"
sleep 5 #sleep so people can ctrl-c if they suspect that the above is false

# First setup directory
mkdir -p exp_data

# Loop over languages and type of data to get all the splits
for lang in en de it nl; do
	for type in gold silver bronze; do
		echo "Extracting $type data for $lang.."
		mkdir -p exp_data/${lang}/${type}/
		# Get the files here
		python src/split_release.py -r data/${lang}/${type}/ -o exp_data/${lang}/${type}/ -l $lang --data_type $type
	done
done

echo "Done -- all files are in exp_data/"

