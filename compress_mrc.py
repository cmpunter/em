#!/usr/bin/python

"""
This program compresses mrc files to the mrcz format and can also extract/decompress mrcz files back to mrc.

NOTE : the decompressed files are almost identical to the original with the following exceptions :
- the mean density is calculated using the minimum and maximum density and is not taken from the original mrc file
- the following header fields are maintained: pixelsize, pixelunits, voltage, C3
- the gain header field is not set in the mrcz file (limitation of the mrcz library code)


Rijksuniversiteit Groningen, 2018
C.M. Punter (c.m.punter@rug.nl)

"""

import argparse
import mrcz
import os


parser = argparse.ArgumentParser(description='Compress MRC files to the MRCZ format while keeping most of the header information')
parser.add_argument('path', nargs='+', help='paths that need to be compressed')
parser.add_argument('-r', '--recursive', help='recursively go through all sub-directories', action='store_true')
parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
parser.add_argument('-d', '--delete', help='delete the original mrc(z) files after writing/reading mrc(z) files', action='store_true')
parser.add_argument('-x', '--extract', help='extract/decompress all mrcz files', action='store_true')
parser.add_argument('-n', '--dry-run', help='dry run', action='store_true')
args = parser.parse_args()


def compress(path):
    global args

    if path.endswith('.mrc'):
        mrcz_path = path[:-4] + '.mrcz'
    elif path.endswith('.mrcs'):
        mrcz_path = path[:-5] + '.mrczs'

    if args.verbose:
        print('compress %s -> %s' % (path, mrcz_path))

        original_size = os.path.getsize(path)
        print('%20s : %d bytes' % ('original size', original_size))

    if not args.dry_run:
        imageData, imageMeta = mrcz.readMRC(path)
        mrcz.writeMRC(imageData, mrcz_path, compressor='zstd', clevel=9, pixelsize=imageMeta['pixelsize'], pixelunits=imageMeta['pixelunits'], voltage=imageMeta['voltage'], C3=imageMeta['C3'], gain=imageMeta['gain'])

        if args.verbose:
            compressed_size = os.path.getsize(mrcz_path)
            ratio = float(original_size) / compressed_size
            print('%20s : %d bytes' % ('compressed size', compressed_size))
            print('%20s : %.2f' % ('compression ratio', ratio))

    if args.delete:
        if args.verbose:
            print('delete %s' % (path))
        if not args.dry_run and os.path.exists(mrcz_path) and os.path.getsize(mrcz_path) > 0:
            os.remove(path)


def extract(path):
    global args

    if path.endswith('.mrcz'):
        mrc_path = path[:-5] + '.mrc'
    elif path.endswith('.mrczs'):
        mrc_path = path[:-6] + '.mrcs'

    if args.verbose:
        print('extract %s -> %s' % (path, mrc_path))
        compressed_size = os.path.getsize(path)
        print('%20s : %d bytes' % ('compressed size', compressed_size))

    if not args.dry_run:
        imageData, imageMeta = mrcz.readMRC(path)
        mrcz.writeMRC(imageData, mrc_path, compressor=None, pixelsize=imageMeta['pixelsize'], pixelunits=imageMeta['pixelunits'], voltage=imageMeta['voltage'], C3=imageMeta['C3'], gain=imageMeta['gain'])

        if args.verbose:
            uncompressed_size = os.path.getsize(mrc_path)
            ratio = float(uncompressed_size) / compressed_size
            print('%20s : %d bytes' % ('uncompressed size', uncompressed_size))
            print('%20s : %.2f' % ('compression ratio', ratio))

    if args.delete:
        if args.verbose:
            print('delete %s' % (path))
        if not args.dry_run and os.path.exists(mrc_path) and os.path.getsize(mrc_path) > 0:
            os.remove(path)


def process(path):
    global args

    if os.path.isfile(path):
        if args.extract and (path.endswith('.mrcz') or path.endswith('.mrczs')):
            extract(path)
        elif not args.extract and (path.endswith('.mrc') or path.endswith('.mrcs')):
            compress(path)
    elif args.recursive and os.path.isdir(path):
        for filename in os.listdir(path):
            process(os.path.join(path, filename))


for path in args.path:
    try:
        if os.path.isdir(path):
            for filename in os.listdir(path):
                process(os.path.join(path, filename))
        elif os.path.isfile(path):
            process(path)
    except:
        print('could not process %s' % path)
