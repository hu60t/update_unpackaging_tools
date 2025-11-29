#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Description : Unpack updater package
"""
import os
import struct
import time
from create_update_package import UPGRADE_FILE_HEADER_LEN
from create_update_package import UPGRADE_COMPINFO_SIZE
from create_update_package import UPGRADE_COMPINFO_SIZE_L2
from create_update_package import COMPONENT_ADDR_SIZE
from create_update_package import COMPONENT_ADDR_SIZE_L2
from create_update_package import UPGRADE_RESERVE_LEN
from create_update_package import UPGRADE_SIGNATURE_LEN

from create_hashdata import HASH_TYPE_SIZE
from create_hashdata import HASH_LENGTH_SIZE
from create_hashdata import HASH_TLV_SIZE
from create_hashdata import UPGRADE_HASHINFO_SIZE
from create_hashdata import CreateHash
from create_hashdata import HashType

from log_exception import UPDATE_LOGGER
from utils import OPTIONS_MANAGER

COMPINFO_LEN_OFFSET = 178
COMPINFO_LEN_SIZE = 2
COMPONENT_ADDR_OFFSET = UPGRADE_FILE_HEADER_LEN
COMPONENT_TYPE_OFFSET = COMPONENT_ADDR_OFFSET + COMPONENT_ADDR_SIZE + 4
COMPONENT_TYPE_OFFSET_L2 = COMPONENT_ADDR_OFFSET + COMPONENT_ADDR_SIZE_L2 + 4
COMPONENT_TYPE_SIZE = 1
COMPONENT_SIZE_OFFSET = 11
COMPONENT_SIZE_SIZE = 4

"""
Format
H: unsigned short
I: unsigned int
B: unsigned char
s: char[]
"""
COMPINFO_LEN_FMT = "H"
COMPONENT_TYPE_FMT = "B"
COMPONENT_SIZE_FMT = "I"


class UnpackPackage(object):
    """
    Unpack the update.bin file
    """

    def __init__(self):
        self.count = 0
        self.component_offset = 0
        self.save_path = None

        if OPTIONS_MANAGER.not_l2:
            self.compinfo_size = UPGRADE_COMPINFO_SIZE
            self.type_offset = COMPONENT_TYPE_OFFSET
            self.addr_size = COMPONENT_ADDR_SIZE
        else:
            self.compinfo_size = UPGRADE_COMPINFO_SIZE_L2
            self.type_offset = COMPONENT_TYPE_OFFSET_L2
            self.addr_size = COMPONENT_ADDR_SIZE_L2

        self.addr_offset = COMPONENT_ADDR_OFFSET
        self.size_offset = self.type_offset + COMPONENT_SIZE_OFFSET

    def check_args(self):
        if not os.access(OPTIONS_MANAGER.unpack_package_path, os.R_OK) and \
            not os.path.exists(self.save_path):
                UPDATE_LOGGER.print_log(
                    "Access unpack_package_path fail! path: %s" % \
                    OPTIONS_MANAGER.unpack_package_path, UPDATE_LOGGER.ERROR_LOG)
                return False
        return True

    def parse_package_file(self, package_file):
        try:
            package_file.seek(COMPINFO_LEN_OFFSET)
            compinfo_len_buffer = package_file.read(COMPINFO_LEN_SIZE)
            compinfo_len = struct.unpack(COMPINFO_LEN_FMT, compinfo_len_buffer)
        except (struct.error, IOError):
            return False

        self.count = compinfo_len[0] // self.compinfo_size
        self.component_offset = UPGRADE_FILE_HEADER_LEN + compinfo_len[0] + UPGRADE_RESERVE_LEN

        try:
            package_file.seek(self.component_offset)
            next_tlv_type_buffer = package_file.read(HASH_TYPE_SIZE)
            next_tlv_type = struct.unpack(COMPINFO_LEN_FMT, next_tlv_type_buffer)
            if next_tlv_type[0] == 0x06:
                UPDATE_LOGGER.print_log("parse update.bin in SDcard package")
                self.component_offset += HASH_TLV_SIZE + UPGRADE_HASHINFO_SIZE + HASH_TYPE_SIZE
                package_file.seek(self.component_offset)
                hashdata_len_buffer = package_file.read(HASH_LENGTH_SIZE)
                hashdata_len = struct.unpack(COMPONENT_SIZE_FMT, hashdata_len_buffer)
                self.component_offset += HASH_LENGTH_SIZE + hashdata_len[0] + HASH_TYPE_SIZE
            elif next_tlv_type[0] == 0x08:
                self.component_offset += HASH_TYPE_SIZE

            package_file.seek(self.component_offset)
            sign_len_buffer = package_file.read(HASH_LENGTH_SIZE)
            sign_len = struct.unpack(COMPONENT_SIZE_FMT, sign_len_buffer)
            UPDATE_LOGGER.print_log(
                "signdata offset:%d length:%d" % (self.component_offset + HASH_LENGTH_SIZE, sign_len[0]))
            self.component_offset += HASH_LENGTH_SIZE + sign_len[0]
        except (struct.error, IOError):
            return False

        UPDATE_LOGGER.print_log("parse package file success! components: %d" % self.count)
        return True

    def parse_component(self, package_file):
        try:
            package_file.seek(self.addr_offset)
            component_addr = package_file.read(self.addr_size)
            component_addr = component_addr.split(b"\x00")[0].decode('utf-8')

            package_file.seek(self.type_offset)
            component_type_buffer = package_file.read(COMPONENT_TYPE_SIZE)
            component_type = struct.unpack(COMPONENT_TYPE_FMT, component_type_buffer)

            package_file.seek(self.size_offset)

            #component_size_buffer = package_file.read(COMPONENT_SIZE_SIZE)
            #component_size = struct.unpack(COMPONENT_SIZE_FMT, component_size_buffer)

            # 修复鸿蒙PC固件system.img超过4GB导致解包不完整的问题
            component_size_buffer = package_file.read(8)
            component_size = struct.unpack('Q', component_size_buffer)

        except (struct.error, IOError):
            UPDATE_LOGGER.print_log(
                "parse component failed!", UPDATE_LOGGER.ERROR_LOG)
            return False, False, False

        return component_addr, component_type[0], component_size[0]

    def create_image_file(self, package_file):
        component_name, component_type, component_size = \
            self.parse_component(package_file)
        if component_name is None or component_type is None or component_size is None:
            UPDATE_LOGGER.print_log("get component_info failed!", UPDATE_LOGGER.ERROR_LOG)
            return False
        component_name = component_name.strip('/')
        if component_name == "version_list":
            component_name = "VERSION.mbn"
        elif component_name == "board_list":
            component_name = "BOARD.list"
        elif component_type == 0:
            component_name = ''.join([component_name, '.img'])
        elif component_type == 1:
            component_name = ''.join([component_name, '.zip'])

        image_file_path = os.path.join(self.save_path, component_name)

        package_file.seek(self.component_offset)

        UPDATE_LOGGER.print_log("component name: %s" % component_name)
        UPDATE_LOGGER.print_log("component offset: %s" % self.component_offset)
        UPDATE_LOGGER.print_log("component size: %s" % component_size)

        image_fd = os.open(image_file_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o755)
        with os.fdopen(image_fd, "wb") as image_file:
            image_buffer = package_file.read(component_size)
            image_file.write(image_buffer)

        self.addr_offset += self.compinfo_size
        self.type_offset += self.compinfo_size
        self.size_offset += self.compinfo_size
        self.component_offset += component_size
        UPDATE_LOGGER.print_log("Create file: %s" % image_file_path)
        return True

    def unpack_package(self):
        """
        Unpack the update.bin file
        return: result
        """
        UPDATE_LOGGER.print_log(
            "Start unpack updater package: %s" % OPTIONS_MANAGER.unpack_package_path)
        filename = ''.join(['unpack_result_', time.strftime("%H%M%S", time.localtime())])
        self.save_path = os.path.join(OPTIONS_MANAGER.target_package, filename)
        os.makedirs(self.save_path)
        
        if not self.check_args():
            UPDATE_LOGGER.print_log(
                "check args failed!", UPDATE_LOGGER.ERROR_LOG)
            return False

        with open(OPTIONS_MANAGER.unpack_package_path, "rb") as package_file:
            if not self.parse_package_file(package_file):
                UPDATE_LOGGER.print_log(
                    "parse package file failed!", UPDATE_LOGGER.ERROR_LOG)
                return False

            for image_id in range(0, self.count):
                UPDATE_LOGGER.print_log("Start to parse component_%d" % image_id)
                if not self.create_image_file(package_file):
                    UPDATE_LOGGER.print_log(
                        "create image file failed!", UPDATE_LOGGER.ERROR_LOG)
                    return False
        return True

