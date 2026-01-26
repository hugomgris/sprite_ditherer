#!/bin/bash

echo "Cleaning up generated sprites"

echo "Cleaning RAW sprites"
rm -rf ./output/raw/thumb
rm -rf ./output/raw/index
rm -rf ./output/raw/middle
rm -rf ./output/raw/ring
rm -rf ./output/raw/pinky

echo "Cleaning DITHERED sprites"
rm -rf ./output/dithered/thumb
rm -rf ./output/dithered/index
rm -rf ./output/dithered/middle
rm -rf ./output/dithered/ring
rm -rf ./output/dithered/pinky

rm -rf ./output/dithered
rm -rf ./output/raw

echo "Removing SPRITESHEETS"
rm -rf ./output/spritesheets

echo "Removing SUMMARY"
rm -rf ./output/*.json

if [ $(ls ./output/raw/thumb/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/dithered/thumb/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/raw/index/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/dithered/index/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/raw/middle/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/dithered/middle/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/raw/ring/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/dithered/ring/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/raw/pinky/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/dithered/pinky/*.png 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/spritesheets 2>/dev/null | wc -l) == 0 ] && \
	[ $(ls ./output/ | wc -l) == 2 ]
then
	echo "cleanup successful"
fi