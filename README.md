# HarmonyOS Update Package `update.bin` Unpacking Tool

```
# Install dependencies
sudo apt install git python3 python3-xmltodict python3-cryptography python3-asn1crypto

# Download the unpacking tool
git clone https://gitcode.com/hu60/update_unpackaging_tools.git

# Extract the full update package
mkdir update_full_base
cd update_full_base
unzip ../update_full_base.zip

# Unpack update.bin
python3 ../update_unpackaging_tools/unpack_update_bin.py -i ./update.bin -o .

# Install dependencies for mounting system.img (skip if the kernel supports erofs natively)
sudo apt install erofsfuse

# Mount system.img
cd ./unpack_result_*
mkdir system
sudo mount -t erofs ./system.img ./system
cd ./system
ls
```

-----------------

# Packaging Tool<a name="EN-US_TOPIC_0000001101934690"></a>

-   [Introduction](#section184mcpsimp)
-   [Directory Structure](#section191mcpsimp)
-   [Description](#section211mcpsimp)
-   [Repositories Involved](#section247mcpsimp)

## Introduction<a name="section184mcpsimp"></a>

The packaging tool is used to prepare an update package. It provides the following functions:

- Creating a full update package: The update package contains only the data necessary for full image update.

- Creating a differential update package: The update package contains only the data necessary for differential image update.

- Creating an update package with changeable partitions: The update package contains the partition table and full image data, which are used for partition change processing and image restoration after partition change.

## Directory Structure<a name="section191mcpsimp"></a>

```
/base/update/packaging_tools
├── lib                         # Dependency libraries of the packaging tool.
├── blocks_manager.py           # BlocksManager class for block management
├── build_update.py             # Access to the packaging tool for differential update packages
├── gigraph_process.py          # Stash for re-sorting the ActionList
├── image_class.py              # Full image and sparse image parsing
├── log_exception.py            # Global log system with custom exceptions
├── patch_package_process.py    # Differential image processing for obtaining patch difference through differential calculation on blocks
├── script_generator.py         # Update script generator
├── transfers_manager.py        # ActionInfo object creation
├── update_package.py           # Update package format management and update package writing
├── utils.py                    # Options management and related functions
└── vendor_script.py            # Extended update scripts
```

## Description<a name="section211mcpsimp"></a>

Running environment:

- Ubuntu 18.04 or later

- Python 3.5 or later

- Python library xmltodict, which is used to parse XML files and needs to be installed independently.

- bsdiff executable program, which performs differential calculation to generate the patch package

- imgdiff executable program, which performs differential calculation on the zip, gz, and lz4 files to generate the patch package

- e2fsdroid executable program, which performs differential calculation to generate the map files of an image

Parameter configuration:

```
Positional arguments:
target_package         Target package file path.
update_package        Update package file path.
Optional arguments:
-h, --help                                                Show this help message and exit.
-s SOURCE_PACKAGE, --source_package SOURCE_PACKAGE        Source package file path.
-nz, --no_zip                                             No zip mode, which means to output update package without zip.
-pf PARTITION_FILE, --partition_file PARTITION_FILE       Variable partition mode, which means to partition list file path.
-sa {ECC,RSA}, --signing_algorithm {ECC,RSA}              Signing algorithms supported by the tool, including ECC and RSA.
-ha {sha256,sha384}, --hash_algorithm {sha256,sha384}     Hash algorithms supported by the tool, including sha256 and sha384.
-pk PRIVATE_KEY, --private_key PRIVATE_KEY                Private key file path.
```

Example code for creating a full update package:

```
python build_update.py ./target/ ./target/package -pk ./target/updater_config/rsa_private_key2048.pem
```

Example code for creating a differential update package:

```
python build_update.py -s source.zip ./target/ ./target/package -pk./target/updater_config/rsa_private_key2048.pem
```

## Repositories Involved<a name="section247mcpsimp"></a>

Update subsystem

**update\_packaging\_tools**

