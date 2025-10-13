#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description: Simple CLI to unpack update.bin using unpack_updater_package.UnpackPackage

Usage example (PowerShell):
  python unpack_update.py -i d:\\path\\to\\update.bin -o d:\\output_dir
  python unpack_update.py --input d:\\update.bin --output d:\\out --not-l2
"""

import argparse
import os
import sys

from log_exception import UPDATE_LOGGER
from unpack_updater_package import UnpackPackage
from utils import OPTIONS_MANAGER, clear_resource


def _check_file(path: str) -> str:
	if not path or not os.path.isfile(path):
		UPDATE_LOGGER.print_log(f"FileNotFoundError, path: {path}", UPDATE_LOGGER.ERROR_LOG)
		return False
	return path


def _ensure_dir(path: str) -> str:
	if os.path.exists(path):
		if not os.path.isdir(path):
			UPDATE_LOGGER.print_log(
				f"Output must be a directory, not a file. path: {path}", UPDATE_LOGGER.ERROR_LOG
			)
			return False
	else:
		try:
			os.makedirs(path, exist_ok=True)
		except OSError:
			UPDATE_LOGGER.print_log(f"Make output directory failed! path: {path}", UPDATE_LOGGER.ERROR_LOG)
			return False
	return path


def parse_args():
	parser = argparse.ArgumentParser(description="Tool for unpacking update.bin")
	parser.add_argument("-i", "--input", required=True, help="Path to update.bin to unpack")
	parser.add_argument("-o", "--output", required=True, help="Directory to place unpacked files")
	parser.add_argument("-nl2", "--not-l2", action="store_true", help="Not L2 mode (use L1 structure)")
	return parser.parse_args()


def main():
	args = parse_args()

	update_bin = _check_file(args.input)
	out_dir = _ensure_dir(args.output)
	if update_bin is False or out_dir is False:
		sys.exit(1)

	# Set global options used by UnpackPackage
	OPTIONS_MANAGER.unpack_package_path = update_bin
	OPTIONS_MANAGER.target_package = out_dir
	OPTIONS_MANAGER.not_l2 = bool(args.not_l2)

	# Execute unpack
	package = UnpackPackage()
	try:
		if not package.unpack_package():
			UPDATE_LOGGER.print_log("Unpack update.bin failed!", UPDATE_LOGGER.ERROR_LOG)
			clear_resource(err_clear=True)
			sys.exit(1)
		UPDATE_LOGGER.print_log("Unpack update.bin success!")
		clear_resource()
		sys.exit(0)
	except Exception:
		# Let global excepthook and our logger handle details
		clear_resource(err_clear=True)
		sys.exit(1)


if __name__ == "__main__":
	main()

