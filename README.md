# Strata 0.2.13 完整离线包

[English](README.en.md)

这个仓库只放打包所需的脚本、补丁、清单、校验和与说明。它不复制上游 [Niko1221/Strata](https://github.com/Niko1221/Strata) 的源码树。安装包在 [Release v0.2.13-offline-r1](https://github.com/Family2002/full-offline-strata-qwen/releases/tag/v0.2.13-offline-r1)。

上游标签是 [v0.2.13](https://github.com/Niko1221/Strata/releases/tag/v0.2.13)，提交 `d2f096475817d4666c364c820b0ca830f751cfc5`。离线入口沿用 [Family2002/Strata#1](https://github.com/Family2002/Strata/pull/1) 和 [#2](https://github.com/Family2002/Strata/pull/2) 的做法，包括 r2 把 `binary_deps.py` 放进 `control/packaging` 的修复。0.2.11 的 r1 第一次启动会报 `No module named binary_deps`。本包不会再出现那个缺文件。

## 版本组合

数字按打进包里的文件填写，不按发布说明的标题改写。

| 部件 | Windows 离线安装包 | Linux 便携包 |
| --- | --- | --- |
| 页面（App Host） | 0.2.13，由标签 v0.2.13 构建 | 同左 |
| Control 压缩包 | `strata-control-0.1.59-windows-x86_64.zip` | `strata-control-0.1.59.1-linux-x86_64.tar.gz` |
| `VERSION` 文件 | 0.1.59 | 0.1.59.1 |
| Terminal 产品版本字符串 | 0.2.13 | 0.2.13.1 |
| 引擎 | 0.1.59 CUDA 12 与 CUDA 13 | 0.1.59 CUDA 12、CUDA 13、SYCL（Intel Arc） |
| Node | 24.12.0 | 24.12.0 |
| llama.cpp | `3cf03257f219afbe7334045ff7c6a06ac68c627d` | 同左 |

Windows 引擎清单里的 notes 仍写着 “0.2.9 NVIDIA”。那是上游压缩包里的原文。文件本身是 v0.2.13 发布的 0.1.59 引擎。

Windows CUDA 12 的驱动门槛是 NVIDIA **576.02**，显卡代码 sm_60、sm_61、sm_70、sm_75、sm_80、sm_86、sm_89，另有 compute_89 的 PTX。CUDA 13 的门槛是 **580.65**，代码 sm_75、sm_86、sm_89、sm_120，另有 compute_120。

Linux CUDA 12 的门槛是 NVIDIA **575.51**（与 Windows 的 576.02 不同，以各自清单为准）。CUDA 13 仍是 **580.65**。SYCL 引擎的 `backend` 是 `sycl`，架构标记是 `intel-arc`。

**关于「Windows / Mac 的 Terminal 仍是 0.2.12」。** 上游 v0.2.13 的更新源里，Control 一项只有 Linux 的 0.1.59.1。在已经安装 0.2.12 的 Windows 上执行 `strata update`，会把引擎升到 0.1.59，并提示 Control 不在这个更新源里，Terminal 因此留在 0.2.12。本仓库的 Windows 包不是那条升级路径。它直接装入 v0.2.13 发布的 Windows Control 0.1.59，这份压缩包自己的 `PRODUCT_VERSION` 是 **0.2.13**，包内 `COMMIT` 是 `d2f096475`。Mac 不在本仓库的交付里。

**0.2.13.1** 是 Linux 桌面在 Intel Arc 上准备模型的修复，写在 v0.2.13 的发布说明里。对应 Control **0.1.59.1**（版本号提交 `b08a069d`，功能提交 `1130d824`，发布压缩包的 `COMMIT` 是 `628f74955a56fcba092495b800dd02af75373a0f`）。Linux 便携包使用这份 Control，所以在 Arc 上不会再停在 “no NVIDIA GPU found”。Windows 包保持 0.1.59，不把这个只针对 Linux 的修复写进 Windows 版本号。引擎没有 0.1.59.1。

## 下载

Release 页面的 `SHA256SUMS.txt` 是校验和的完整列表。单个文件超过约 1900 MiB 时会分成 `*.part-00`、`*.part-01`……拼回方法：

```sh
sh packaging/reassemble.sh Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
```

或：

```sh
cat Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-* > Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
sha256sum -c SHA256SUMS.txt
```

Windows 安装包如果没有分卷，就是一个 `.exe`。草稿如果单独成包，文件名含 `drafts`。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `Strata-0.2.13-offline-r1-windows-x64-cuda12-cuda13-setup.exe` | 1,697,218,945 | `c2c6f3bf2de97a86c1d92505836323c6336f7666fdf475e0e03d382bb088fe90` |
| `Strata-0.2.13-offline-r1-drafts.tar` | 2,550,261,760 | `89aa4b837fb491dd8a1f95b5d519473686eff7a9279616314c966174b9a812bd` |
| `Strata-0.2.13-offline-r1-drafts.tar.part-00` | 1,992,294,400 | `5ba7feb3ba9a3e99554b57505977aab894e703197ff2079199745780e8c2e401` |
| `Strata-0.2.13-offline-r1-drafts.tar.part-01` | 557,967,360 | `f48c6e1d887a82658abdb1b1918f7690571cdfb3439a9d77f7aaee5533ddc6d2` |
| `Strata-0.2.13-offline-r1-linux-x86_64-portable.tar` | 6,677,780,480 | `130714284052f2738f2dae94ea401225d726660cd0dc3e63201b1087944a6efa` |
| `Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-00` | 1,992,294,400 | `6ac3ee9d3c05ea37ab0bc93d576e758d790f01d003cb055cda90fe039b9d559b` |
| `Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-01` | 1,992,294,400 | `7956a1f094882a24000bb914f86b3d0ac3b5c949dc34d45a57e9476420fc92d2` |
| `Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-02` | 1,992,294,400 | `e3f498e5dbec072088888bfbd75dac45139682eb2de91cb2a0bd37323e70e52e` |
| `Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-03` | 700,897,280 | `e4b9f97db3dc77ca3f1e57f8e92922062e6e7f2d7673b5a9ca25b5724f5f16dc` |

Windows 的 exe 小于 2 GB，Release 里是一整份。草稿 tar 和 Linux tar 超过限制，Release 里是分卷；拼回后的 SHA-256 是表里不带 `.part-` 的那一行。仓库里的 [SHA256SUMS.txt](SHA256SUMS.txt) 与 Release 上的同名文件一致。

本 Release 的草稿包里包含 stock Q4_0 pack 和它的 selector 转换，哈希与上游钉死的值一致。`data/mtp/rt/experts.bin` 为 707,788,800 字节，SHA-256 `09398406be61f1f54c93861f449e48b8df0bfccbc9ec9b2b7636775a6ea9244f`。

## 离线安装与第一次启动

目标电脑不需要联网。安装和第一次打开不会运行 winget、pip、git、cmake，也不会安装 WebView2、另一份 Python、另一份 Node、VC++ 或 CUDA Toolkit。缺文件时程序打印路径并退出，状态码 5，不会去下载补齐。

显卡驱动要系统自己有。Windows 需要 NVIDIA 驱动。Linux 需要 NVIDIA 驱动（CUDA）或 Intel GPU 的 Level Zero 驱动（SYCL）。本包不安装驱动。浏览器要系统里已经有。

模型权重不在包里。只准备架构为 `qwen4exp` 的 GGUF（Qwen3.8-Flash-Next）。DeepSeek 的 `strata-dsv41` 不在包里，选了会被拒绝。图片编码器（mmproj）如果本地没有，就保持关闭，不会下载。

### Windows

1. 运行 `Strata-0.2.13-offline-r1-windows-x64-cuda12-cuda13-setup.exe`。它装到 `%LOCALAPPDATA%\StrataOffline`，不请求管理员权限。
2. 把草稿包解进同一目录，使下面两个目录出现：
   - `%LOCALAPPDATA%\StrataOffline\data\dflash2\`
   - `%LOCALAPPDATA%\StrataOffline\data\mtp\rt\`
3. 运行 `%LOCALAPPDATA%\StrataOffline\Start-Strata.cmd`。
4. 用这台电脑上已有的浏览器打开它打印的 `http://127.0.0.1:8791/`。
5. 在页面里选择已经放在本机的 GGUF，或 `Start-Strata.cmd --model D:\models\qwen`。

两套 CUDA 引擎分目录存放。读到显卡代码并且两套都符合清单时用 CUDA 13；达不到就用 CUDA 12。没有读到计算能力时不猜 CUDA 13。`Start-Strata.cmd --cuda 12` 或 `--cuda 13` 可指定，不符合清单就退出。安装在电脑里的 CUDA Toolkit 不会被当成驱动，含有 cublas/cudart 的目录会从这次启动的 PATH 里去掉。

再安装到同一个目录会盖过旧文件。NSIS 脚本没有卸载程序。删掉 `%LOCALAPPDATA%\StrataOffline` 即可移除这套文件。桌面上的快捷方式要另行删除。

### Linux

```sh
tar -xf Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
cd Strata-0.2.13-offline-r1-linux-x86_64
./Start-Strata.sh
```

草稿已经在这个目录的 `data/` 里，不必再解第二个包。没有 NVIDIA 驱动、并且包里有 SYCL 引擎时，启动选用 SYCL。`./Start-Strata.sh --cuda 12`、`--cuda 13` 或 `--cuda sycl` 可指定。AMD 的 HIP 引擎不在这个包里。

这不是 AppImage。0.2.13.1 的 Arc 修复在所带的 Control 0.1.59.1 里，准备模型时走这份 Control。

## MTP 与 DFlash2

页面的 **Drafting** 有四项：Auto、MTP、DFlash2、Off。终端的准备屏幕是同一选项。写进模型运行配置的字段是 `"drafting"`，取值 `auto`、`mtp`、`dflash2`、`off`。

数据目录由离线入口写成安装目录下的 `data/`（`offline-settings.json` 的 `data_dir`）。不要把它指到别的空目录，否则下面这些文件不会被用到。

### 需要哪些文件

都在 `data/` 下：

| 文件 | 作用 |
| --- | --- |
| `dflash2/qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack` | 上游发布的 tuned DFlash2，339,694,592 字节，约 0.32 GiB（说明里的约 0.34 GB）。CUDA / HIP 在启用 tuned 且引擎能读 Q4_0 selector 时用它。SHA-256 `4df2e5ab2b47c064afbe662e16e4f06569877125c2d0e2123a4ac755266c664c` |
| `dflash2/qwen3.8-flash-next-dflash2.strata1.q4_0-bf16sel.pack` | 同一发布里的 bf16 selector 版，522,458,112 字节。SYCL（Intel Arc）读这个，不读 selq4。SHA-256 `34ca17fee701ff088b6069acc35a26661d237953f5d114be0a3f7dae3ec5cda9` |
| `dflash2/qwen3.8-flash-next-dflash2.q4_0.pack` | 没有 tuned 条目的模型集合用的 stock pack。上游不发布这个文件，而是从 1.2 GB 的 safetensors 在本地打出来。本仓库只在打出的字节与上游固定的 SHA-256 `cda40d62d0eb8f37ed6e272142641a1d2f0de4a32f9e14d0416e7a71534849f1` 一致时才放进包里 |
| `dflash2/qwen3.8-flash-next-dflash2.q4_0-selq4.pack` | 由上一文件在本地转换 selector 得到，SHA-256 必须是 `4a42b98220ea7880664002c8edda1563aecbae754b762a2e2f31b2b91ee93ecd`。它和 strata1 的 selq4 不是同一个文件 |
| `dflash2/draft_vocab.bin` 以及 `_en`、`_fr`、`_cyrillic` | 随 Control 带的草稿词表 |
| `mtp/rt/experts.bin`、`dense.bin`、`dense.txt`、`draft_vocab.bin` | 由上游固定修订版的 MTP 张量打成 Q2_0 运行时。引擎读这个目录，不读那 5 GB 原始张量 |

`experts.bin` 为 707,788,800 字节。这是 `tools/mtp_rt.py` 对 512 个专家写出的固定布局。

### 离线时怎么退回

离线入口设置 `STRATA_OFFLINE_ENTRY=1`。在这个值下：

-  tuned pack 的大小和 SHA-256 已经对上时，直接使用，不再访问更新源。
-  stock pack 已经在 `data/dflash2/` 并且哈希正确时，`strata drafting fetch` 认为草稿已就绪，不再下载那 1.2 GB。
-  应该使用的 DFlash2 文件不在时，准备停止，并说明 “The DFlash2 drafter is not in the offline folder. Nothing was downloaded.” 不会改去联网。
-  选择 MTP 而 `data/mtp/rt/experts.bin` 不在时，准备停止，并说明离线入口不会下载草稿层。不会改去 Hugging Face 拉取那约 5 GB。
-  选 Off，或 Auto 在这块卡上的测量结果是 MTP、而 MTP 文件在，则走 MTP，不要求 DFlash2。
-  Auto 在 12 GB 级别等卡片上本来就用 MTP（上游 `CLASS_DEFAULTS`）。gfx1201（RX 9070 一类）的 Auto 也用 MTP，因为 DFlash2 的 prompt stall 仍是上游已知问题；手动选 DFlash2 仍会尝试 DFlash2。

本包没有 HIP 引擎，所以上面 HIP 的默认只在你另外放入 HIP 引擎时才有意义。

### 怎样确认已经生效

1. 启动后的引擎命令行里：
   - DFlash2：同时有 `--draft dflash2`、`--draft-model`，并且路径落在 `data/dflash2/` 里上述某个 pack。
   - MTP：有 `--mtp`，路径是 `data/mtp/rt`（或 `--mtp-draft-vocab` 指向该目录里的 `draft_vocab.bin`）。
   - 关闭：没有这两类参数。
2. 页面模型状态里的 drafting 说明，与上面的选项一致。
3. 在安装目录执行（Windows 把 `python3` 换成 `control\python\python.exe`）：

```sh
./control/python/bin/python3 ./control/strata.py drafting plan --data-dir "$PWD/data" --mode dflash2 --output json
```

`needed` 为 false，表示它认定文件已经在本地。若为 true，就是还缺文件，离线时不要指望它自己去下。

## 重新打包

需要：Linux、Python 3.12、Node（用来构建页面；上游要求 Node ≥ 24.12.0，构建机上的 Node 22 也能跑完 `vite build`）、makensis、curl、tar。

```sh
python3 packaging/build_offline_release.py
```

脚本会克隆标签 v0.2.13，打上 `patches/offline-entry-v0.2.13.patch`，Linux 再打上 `patches/linux-control-0.1.59.1.patch`，核对 [packaging/PINS.md](packaging/PINS.md) 里的 SHA-256，然后做安装包。已经准备好的源码树和下载缓存可以用 `STRATA_SRC`、`STRATA_LINUX_SRC`、`STRATA_CACHE` 指过去。

## 已知限制

- 只在打包机上做了导入闭包检查和离线入口的单元测试（23 项）。没有在 Windows 上安装这个 exe，没有在 GPU 上跑推理。
- 模型权重不在包里。第一次 “Preparing your model” 仍可能要数分钟，这是上游 0.2.13 已知的准备时间，不是还在下载运行库。
- 没有 DeepSeek 引擎，没有 AMD HIP 引擎，没有 Mac 包。
- NSIS 安装包没有卸载程序。Windows 的草稿在单独的压缩包里，因为把引擎和全部草稿放进同一个 exe 会越过 NSIS / GitHub 单文件约 2 GB 的限制。Linux 便携包把草稿打在里面；若 tar 超过限制，Release 里是分卷。
- `binary_deps` 能看到 PE 的导入表和延迟加载。按裸文件名 `LoadLibrary` 的调用不在这张表里。
- 一个会忽略环境变量、自己打开网络的子进程，离线策略拦不住。入口自己的下载路径在 `STRATA_OFFLINE_ENTRY=1` 时会拒绝 http(s)。
