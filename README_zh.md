# 鸿蒙更新包 update.bin 解包工具

```
# 安装依赖
sudo apt install git python3 python3-xmltodict python3-cryptography python3-asn1crypto

# 下载解包工具
git clone https://gitcode.com/hu60/update_unpackaging_tools.git

# 解压全量更新包
mkdir update_full_base
cd update_full_base
unzip ../update_full_base.zip

# 解包 update.bin
../update_unpackaging_tools/unpack_update_bin.py -i ./update.bin -o .

# 安装挂载 system.img 所需依赖包（如果内核直接支持erofs文件系统则无需安装）
sudo apt install erofsfuse

# 挂载system.img
cd ./unpack_result_*
mkdir system
sudo mount -t erofs ./system.img ./system
cd ./system
ls
```

-----------------

# 升级包制作工具<a name="ZH-CN_TOPIC_0000001101934690"></a>

-   [简介](#section184mcpsimp)
-   [目录](#section191mcpsimp)
-   [约束](#section120mcpsimp)
-   [说明](#section211mcpsimp)
    -   [使用说明](#section220mcpsimp)

-   [相关仓](#section247mcpsimp)

## 简介<a name="section184mcpsimp"></a>

升级包制作工具是用于制作升级包的工具，功能主要包括：全量升级包制作、差分升级包制作以及变分区升级包制作。

- 全量升级包制作：升级包中只包括镜像全量升级相关数据，用于镜像全量升级；

- 差分升级包制作：升级包中只包括镜像差分升级相关数据，用于镜像差分升级；

- 变分区升级包：升级包中包括分区表、镜像全量数据，用于变分区处理和变分区后的镜像恢复。

更多升级子系统相关概念，请参考：[升级子系统](https://gitcode.com/openharmony/docs/blob/master/zh-cn/readme/%E5%8D%87%E7%BA%A7%E5%AD%90%E7%B3%BB%E7%BB%9F.md)

## 目录<a name="section191mcpsimp"></a>

```
/base/update/packaging_tools
├── lib                         # 制作升级包工具依赖库目录
├── blocks_manager.py           # BlocksManager类定义，用于block块管理
├── build_update.py             # 差分包制作工具入口代码，入口参数定义
├── build_pkcs7.py              # 升级包签名
├── create_update_package.py    # 升级包制作
├── gigraph_process.py          # 生成Stash，重置ActionList的顺序
├── image_class.py              # 全量镜像、稀疏镜像解析处理
├── log_exception.py            # 全局log系统定义，自定义exception
├── patch_package_process.py    # 差分镜像处理，Block差分获取patch差异
├── script_generator.py         # 升级脚本生成器
├── transfers_manager.py        # 创建ActionInfo对象
├── unpack_update_package.py    # 升级包反解
├── update_package.py           # 升级包格式管理、升级包写入
├── utils.py                    # Options管理,其他相关功能函数定义
└── vendor_script.py            # 厂商升级流程脚本扩展
```

## 约束<a name="section120mcpsimp"></a>

工具运行环境配置：

- Ubuntu18.04或更高版本系统；

- python3.5及以上版本；

- python库xmltodict， 解析xml文件，需要单独安装；

## 说明<a name="section211mcpsimp"></a>

### 使用说明<a name="section220mcpsimp"></a>

- bsdiff可执行程序，差分计算，比较生成patch；

- imgdiff可执行程序，差分计算，针对zip、gz、lz4类型的文件，对比生成patch；

- e2fsdroid可执行程序，差分计算，用于生成镜像的map文件。

工具参数配置说明：

```
positional arguments:
target_package         Target package file path.
update_package        Update package file path.
optional arguments:
-h, --help                                                show this help message and exit
-s SOURCE_PACKAGE, --source_package SOURCE_PACKAGE        Source package file path.
-nz, --no_zip                                             No zip mode, Output update package without zip.
-pf PARTITION_FILE, --partition_file PARTITION_FILE       Variable partition mode, Partition list file path.
-sa {ECC,RSA}, --signing_algorithm {ECC,RSA}              The signing algorithm supported by the tool include['ECC', 'RSA'].
-ha {sha256,sha384}, --hash_algorithm {sha256,sha384}     The hash algorithm  supported by the tool include ['sha256', 'sha384'].
-pk PRIVATE_KEY, --private_key PRIVATE_KEY                Private key file path.
```

全量升级包制作命令示例：

```
python build_update.py ./target/ ./target/package -pk ./target/updater_config/rsa_private_key2048.pem
```

差分升级包制作命令示例：

```
python build_update.py -s source.zip ./target/ ./target/package -pk./target/updater_config/rsa_private_key2048.pem
```

## 相关仓<a name="section247mcpsimp"></a>

[升级子系统](https://gitcode.com/openharmony/docs/blob/master/zh-cn/readme/%E5%8D%87%E7%BA%A7%E5%AD%90%E7%B3%BB%E7%BB%9F.md)

[**update\_packaging\_tools**](https://gitcode.com/openharmony/update_packaging_tools)

