# Strata 0.2.13 full offline packages

[中文](README.md)

This repository holds the packaging scripts, patches, pin list, checksums, and docs. It does not copy the upstream [Niko1221/Strata](https://github.com/Niko1221/Strata) tree. The installers are on [Release v0.2.13-offline-r1](https://github.com/Family2002/full-offline-strata-qwen/releases/tag/v0.2.13-offline-r1).

The upstream tag is [v0.2.13](https://github.com/Niko1221/Strata/releases/tag/v0.2.13), commit `d2f096475817d4666c364c820b0ca830f751cfc5`. The offline entry follows [Family2002/Strata#1](https://github.com/Family2002/Strata/pull/1) and [#2](https://github.com/Family2002/Strata/pull/2), including the r2 fix that places `binary_deps.py` in `control/packaging`. The 0.2.11 r1 installer stopped on first start with `No module named binary_deps`. This package includes that file.

## Versions

The numbers are the ones inside the files that were packed.

| Piece | Windows installer | Linux portable tree |
| --- | --- | --- |
| App Host page | 0.2.13, built from tag v0.2.13 | same |
| Control archive | `strata-control-0.1.59-windows-x86_64.zip` | `strata-control-0.1.59.1-linux-x86_64.tar.gz` |
| `VERSION` file | 0.1.59 | 0.1.59.1 |
| Terminal product string | 0.2.13 | 0.2.13.1 |
| Engines | 0.1.59 CUDA 12 and CUDA 13 | 0.1.59 CUDA 12, CUDA 13, and SYCL (Intel Arc) |
| Node | 24.12.0 | 24.12.0 |
| llama.cpp | `3cf03257f219afbe7334045ff7c6a06ac68c627d` | same |

The notes field inside the Windows engine manifests still says "0.2.9 NVIDIA". That string is upstream's. The files are the 0.1.59 engines from the v0.2.13 release.

Windows CUDA 12 requires NVIDIA driver **576.02** and covers sm_60, sm_61, sm_70, sm_75, sm_80, sm_86, sm_89, plus compute_89 PTX. CUDA 13 requires **580.65** and covers sm_75, sm_86, sm_89, sm_120, plus compute_120.

Linux CUDA 12 requires NVIDIA driver **575.51** (the Windows floor is 576.02; each manifest is its own). CUDA 13 is **580.65**. The SYCL package has `backend` `sycl` and arch `intel-arc`.

**"Windows and Mac Terminal stay on 0.2.12."** The v0.2.13 update feed lists a Control package only for Linux (0.1.59.1). On a Windows machine that already has 0.2.12, `strata update` moves the engine to 0.1.59 and says Control is not in that feed, so the Terminal stays 0.2.12. This Windows package is not that upgrade. It installs the published Windows Control 0.1.59, whose own `PRODUCT_VERSION` is **0.2.13** and whose `COMMIT` file is `d2f096475`. No Mac build is published from this repository.

**0.2.13.1** is the Linux desktop fix for preparing a model on Intel Arc, described in the v0.2.13 release notes. It is Control **0.1.59.1** (version bump `b08a069d`, behaviour change `1130d824`, `COMMIT` inside the published archive `628f74955a56fcba092495b800dd02af75373a0f`). The Linux portable tree uses that Control, so Arc setup does not stop at "no NVIDIA GPU found". The Windows package stays on 0.1.59. There is no 0.1.59.1 engine.

## Download

`SHA256SUMS.txt` on the release is the full checksum list. A file over about 1900 MiB is split into `*.part-00`, `*.part-01`, and so on:

```sh
sh packaging/reassemble.sh Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
```

or:

```sh
cat Strata-0.2.13-offline-r1-linux-x86_64-portable.tar.part-* > Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
sha256sum -c SHA256SUMS.txt
```

The Windows installer is one `.exe` when it fits. Drafters, when they are a separate archive, have `drafts` in the name.

| File | Bytes | SHA-256 |
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

The Windows exe is under 2 GB, so the release stores it whole. The drafter tar and the Linux tar are split; the SHA-256 of the rejoined file is the row without `.part-`. [SHA256SUMS.txt](SHA256SUMS.txt) in this repository matches the file on the release.

This release's drafter archive does include the stock Q4_0 pack and its selector conversion; both match the hashes upstream pins. `data/mtp/rt/experts.bin` is 707,788,800 bytes, SHA-256 `09398406be61f1f54c93861f449e48b8df0bfccbc9ec9b2b7636775a6ea9244f`.

## Offline install and first start

The target machine does not need a network. Install and first start do not run winget, pip, git, cmake, or a WebView2 installer, and they do not install another Python, Node, the Visual C++ redistributable, or the CUDA toolkit. A missing file is printed and the process exits with status 5. Nothing is downloaded to fill the gap.

The graphics driver has to be the machine's own. Windows needs an NVIDIA driver. Linux needs an NVIDIA driver (CUDA) or the Intel GPU Level Zero driver (SYCL). This package does not install a driver. The browser has to be one the machine already has.

Model weights are not included. Preparation handles a GGUF whose architecture is `qwen4exp` (Qwen3.8-Flash-Next). The DeepSeek `strata-dsv41` engine is not included and that architecture is refused. A picture encoder (mmproj) stays off when it is not already local.

### Windows

1. Run `Strata-0.2.13-offline-r1-windows-x64-cuda12-cuda13-setup.exe`. It installs to `%LOCALAPPDATA%\StrataOffline` without asking for an administrator.
2. Extract the drafter archive into that same directory so these two folders exist:
   - `%LOCALAPPDATA%\StrataOffline\data\dflash2\`
   - `%LOCALAPPDATA%\StrataOffline\data\mtp\rt\`
3. Run `%LOCALAPPDATA%\StrataOffline\Start-Strata.cmd`.
4. Open the printed `http://127.0.0.1:8791/` in a browser already on the PC.
5. Pick a local GGUF in the page, or start with `Start-Strata.cmd --model D:\models\qwen`.

The two CUDA engines stay in separate directories. When the GPU code was read and both manifests accept the card and the driver, CUDA 13 is used. Otherwise CUDA 12 is used. An unreported compute capability does not select CUDA 13. `Start-Strata.cmd --cuda 12` or `--cuda 13` forces one package; a choice the manifest rejects exits. A CUDA toolkit installed on the PC is not treated as the driver, and a directory that contains cublas or cudart DLLs is removed from PATH for this start.

Installing again into the same directory overwrites the old files. The NSIS script has no uninstaller. Delete `%LOCALAPPDATA%\StrataOffline`. The desktop shortcut is separate.

### Linux

```sh
tar -xf Strata-0.2.13-offline-r1-linux-x86_64-portable.tar
cd Strata-0.2.13-offline-r1-linux-x86_64
./Start-Strata.sh
```

Drafters are already under `data/`. When no NVIDIA driver is reported and the SYCL engine is present, that engine is selected. `./Start-Strata.sh --cuda 12`, `--cuda 13`, or `--cuda sycl` forces one. AMD HIP engines are not in this tree.

This is not the AppImage. The 0.2.13.1 Arc fix is the bundled Control 0.1.59.1, which is what model setup runs.

## MTP and DFlash2

The page's **Drafting** control is Auto, MTP, DFlash2, or Off. The Terminal's drafting screen is the same choice. The run config field is `"drafting"`, one of `auto`, `mtp`, `dflash2`, `off`.

The offline entry writes `data_dir` to the `data/` folder inside the install (`offline-settings.json`). Pointing that setting at some other empty folder hides the files below.

### Files

All of these live under `data/`:

| File | Role |
| --- | --- |
| `dflash2/qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack` | Tuned DFlash2 from the upstream release, 339,694,592 bytes (about 0.32 GiB; the notes say about 0.34 GB). Used when a tuned CUDA or HIP entry applies and the engine reads Q4_0 selector rows. SHA-256 `4df2e5ab2b47c064afbe662e16e4f06569877125c2d0e2123a4ac755266c664c` |
| `dflash2/qwen3.8-flash-next-dflash2.strata1.q4_0-bf16sel.pack` | The bf16-selector tuned file from the same release, 522,458,112 bytes. The SYCL engine reads this one and refuses selq4. SHA-256 `34ca17fee701ff088b6069acc35a26661d237953f5d114be0a3f7dae3ec5cda9` |
| `dflash2/qwen3.8-flash-next-dflash2.q4_0.pack` | Stock pack for sets that have no tuned entry. Upstream does not publish it; it is packed locally from the 1.2 GB safetensors file. This repository includes it only when the bytes match SHA-256 `cda40d62d0eb8f37ed6e272142641a1d2f0de4a32f9e14d0416e7a71534849f1` |
| `dflash2/qwen3.8-flash-next-dflash2.q4_0-selq4.pack` | Selector conversion of that stock pack. Required SHA-256 `4a42b98220ea7880664002c8edda1563aecbae754b762a2e2f31b2b91ee93ecd`. It is not the strata1 selq4 file |
| `dflash2/draft_vocab.bin` and the `_en`, `_fr`, `_cyrillic` copies | Draft vocabularies shipped with Control |
| `mtp/rt/experts.bin`, `dense.bin`, `dense.txt`, `draft_vocab.bin` | MTP runtime packed at Q2_0 from the pinned checkpoint tensors. The engine reads this directory, not the 5 GB of raw tensors |

`experts.bin` is 707,788,800 bytes. That is the fixed layout `tools/mtp_rt.py` writes for 512 experts.

### What happens offline

The entry sets `STRATA_OFFLINE_ENTRY=1`. While that is set:

- A tuned pack whose size and SHA-256 already match is used. The update feed is not contacted.
- A stock pack that is already in `data/dflash2/` with the right hash counts as ready, so `strata drafting fetch` does not download the 1.2 GB safetensors file.
- If the DFlash2 file that this choice needs is absent, setup stops with "The DFlash2 drafter is not in the offline folder. Nothing was downloaded." It does not switch to the network.
- If MTP is selected and `data/mtp/rt/experts.bin` is absent, setup stops and says the offline entry does not download the draft layer. It does not fetch the ~5 GB from Hugging Face.
- Off, or Auto on a card whose measured default is MTP when those MTP files are present, uses MTP and does not require DFlash2.
- Auto on the 12 GB class uses MTP (upstream `CLASS_DEFAULTS`). Auto on gfx1201 (RX 9070 class) also uses MTP because the DFlash2 prompt stall is still an upstream known problem. Choosing DFlash2 by hand still tries DFlash2.

This package has no HIP engine, so the HIP defaults matter only if you add one yourself.

### How to see that it is on

1. The engine command line:
   - DFlash2: `--draft dflash2` and `--draft-model` pointing at one of the packs under `data/dflash2/`.
   - MTP: `--mtp` pointing at `data/mtp/rt` (or `--mtp-draft-vocab` pointing at `draft_vocab.bin` in that directory).
   - Off: neither.
2. The drafting note on the model in the page matches that choice.
3. From the install directory (on Windows, `control\python\python.exe` instead of the path below):

```sh
./control/python/bin/python3 ./control/strata.py drafting plan --data-dir "$PWD/data" --mode dflash2 --output json
```

`needed: false` means the file is already local. `needed: true` means it is still missing. Offline, it will not fetch itself.

## Rebuilding

Needs Linux, Python 3.12, Node (upstream asks for Node ≥ 24.12.0; `vite build` also completed here on Node 22), makensis, curl, and tar.

```sh
python3 packaging/build_offline_release.py
```

The script clones tag v0.2.13, applies `patches/offline-entry-v0.2.13.patch`, applies `patches/linux-control-0.1.59.1.patch` for the Linux tree, checks the SHA-256 list in [packaging/PINS.md](packaging/PINS.md), and packs. `STRATA_SRC`, `STRATA_LINUX_SRC`, and `STRATA_CACHE` reuse a tree and a download cache that are already on disk.

## Limits

- Import closure and the offline-entry unit tests (23) were run on the build machine. The exe was not installed on Windows, and no GPU inference was run.
- Model weights are not included. The first "Preparing your model" step can still take several minutes. That wait is the one upstream recorded for 0.2.13. It is not a missing runtime being downloaded.
- No DeepSeek engine, no AMD HIP engine, no Mac package.
- The NSIS script has no uninstaller. Windows drafters are a second archive, because putting both engines and every drafter into one exe crosses the NSIS and GitHub per-file limit around 2 GB. The Linux portable tree contains the drafters. If that tar is over the limit, the release stores pieces.
- `binary_deps` reads the PE import table, including delay-load imports. A `LoadLibrary` of a bare name is not in that table.
- A child process that ignores the environment and opens a socket on its own is not stopped. The entry's own download paths refuse http(s) while `STRATA_OFFLINE_ENTRY=1`.
