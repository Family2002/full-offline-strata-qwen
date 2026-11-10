#!/usr/bin/env python3
"""Build the v0.2.13 offline Windows installer and Linux portable tree.

The script clones Niko1221/Strata tag v0.2.13, applies the patches in ../patches,
downloads the pinned upstream binaries, and packs them. It does not commit those
binaries. A machine that already has the patched trees and the download cache can
reuse them:

    STRATA_SRC=/tmp/strata-v0213 STRATA_LINUX_SRC=/tmp/strata-linux-src \\
    STRATA_CACHE=/tmp/strata-cache python3 packaging/build_offline_release.py

The target PC does not run this script. Nothing here installs a GPU driver.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_OFFLINE = ROOT / "patches" / "offline-entry-v0.2.13.patch"
PATCH_LINUX = ROOT / "patches" / "linux-control-0.1.59.1.patch"
CACHE = Path(os.environ.get("STRATA_CACHE", "/tmp/strata-offline-cache-0213"))
WORK = Path(os.environ.get("STRATA_WORK", "/tmp/strata-offline-work-0213"))
OUT = Path(os.environ.get("STRATA_OUT", "/tmp/strata-offline-out-0213"))
UPSTREAM = "https://github.com/Niko1221/Strata.git"
TAG = "v0.2.13"
TAG_COMMIT = "d2f096475817d4666c364c820b0ca830f751cfc5"
RELEASE = "https://github.com/Niko1221/Strata/releases/download/v0.2.13/"
PART = 1900 * 1024 * 1024  # under GitHub's 2 GiB asset limit

PINS = {
    "node-win.zip": (
        "https://nodejs.org/dist/v24.12.0/node-v24.12.0-win-x64.zip",
        "9c125f61ae947b52e779095830f9cac267846a043ef7192183c84016aaad2812",
    ),
    "node-linux.tar.gz": (
        "https://nodejs.org/dist/v24.12.0/node-v24.12.0-linux-x64.tar.gz",
        "6159227e0af7d7c3c6bb2fa900452b04a6cb8841a702a79acc613209d70b04d0",
    ),
    "llama.zip": (
        "https://github.com/ggml-org/llama.cpp/archive/3cf03257f219afbe7334045ff7c6a06ac68c627d.zip",
        "cbe23c594282ead2937abb3f008e51fcec4609d9256652fff42c7cc1c21ea47b",
    ),
    "control-win.zip": (
        RELEASE + "strata-control-0.1.59-windows-x86_64.zip",
        "c81f6800094942a5e750c7d93f348062bc16484f946ea83b0c0d2f8c91c44e87",
    ),
    "control-linux.tar.gz": (
        RELEASE + "strata-control-0.1.59.1-linux-x86_64.tar.gz",
        "73fb612848cf00fa1072623029b35405bbbb63e3f4c688fe6f38c78e3fc022ac",
    ),
    "engine-win-cuda12.tar.gz": (
        RELEASE + "strata-engine-0.1.59-windows-x86_64-cuda-cuda12.tar.gz",
        "934ac7f321e89a8935c26037ff32fcc0acce526e492c544b98aaf5dec86dbe46",
    ),
    "engine-win-cuda13.tar.gz": (
        RELEASE + "strata-engine-0.1.59-windows-x86_64-cuda-cuda13.tar.gz",
        "3f071a7ccbbf3dcdefed8bff777896d8dd0b580417a078154a7d2c2402ec4158",
    ),
    "engine-linux-cuda12.tar.gz": (
        RELEASE + "strata-engine-0.1.59-linux-x86_64-cuda-cuda12.tar.gz",
        "4bf321cb0c2d7ff15fe221f22a29aeb8371f24fa77a4425c920eb01a520babbc",
    ),
    "engine-linux-cuda13.tar.gz": (
        RELEASE + "strata-engine-0.1.59-linux-x86_64-cuda-cuda13.tar.gz",
        "42ab04fa3201e41bef5fac28c05f5c35c909419ec937d879b505bf1516742610",
    ),
    "engine-linux-sycl.tar.gz": (
        RELEASE + "strata-engine-0.1.59-linux-x86_64-sycl.tar.gz",
        "8b2586ab57a2ad8df593d11dc6a3509620ca49fb352692ae0f7f4f7d014a7839",
    ),
    "dflash-selq4.pack": (
        RELEASE + "qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack",
        "4df2e5ab2b47c064afbe662e16e4f06569877125c2d0e2123a4ac755266c664c",
    ),
    "dflash-bf16sel.pack": (
        RELEASE + "qwen3.8-flash-next-dflash2.strata1.q4_0-bf16sel.pack",
        "34ca17fee701ff088b6069acc35a26661d237953f5d114be0a3f7dae3ec5cda9",
    ),
}

WIN_ENGINES = {
    "engine-win-cuda12.tar.gz": "0.1.59-windows-x86_64-cuda-cuda12",
    "engine-win-cuda13.tar.gz": "0.1.59-windows-x86_64-cuda-cuda13",
}
LINUX_ENGINES = {
    "engine-linux-cuda12.tar.gz": "0.1.59-linux-x86_64-cuda-cuda12",
    "engine-linux-cuda13.tar.gz": "0.1.59-linux-x86_64-cuda-cuda13",
    "engine-linux-sycl.tar.gz": "0.1.59-linux-x86_64-sycl",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(name: str) -> Path:
    url, want = PINS[name]
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / name
    if dest.is_file() and sha256(dest) == want:
        print(f"cached {name}", flush=True)
        return dest
    print(f"downloading {url}", flush=True)
    part = dest.with_suffix(dest.suffix + ".part")
    subprocess.run(["curl", "-fL", "--retry", "5", "--retry-all-errors", "-o", str(part), url], check=True)
    got = sha256(part)
    if got != want:
        part.unlink(missing_ok=True)
        raise SystemExit(f"{name} hash {got} != {want}")
    part.replace(dest)
    return dest


def copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.map"))


def prepare_source(env_name: str, dest: Path, extra_patch: Path | None) -> Path:
    given = os.environ.get(env_name)
    if given:
        path = Path(given)
        if not (path / "strata_control" / "windows_offline.py").is_file():
            raise SystemExit(f"{env_name}={path} has no offline entry")
        print(f"reuse {env_name} {path}", flush=True)
        return path
    if dest.exists() and (dest / "strata_control" / "windows_offline.py").is_file() and extra_patch is None:
        return dest
    if dest.exists():
        shutil.rmtree(dest)
    print(f"cloning {TAG} into {dest}", flush=True)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", TAG, UPSTREAM, str(dest)], check=True)
    subprocess.run(["git", "apply", "--whitespace=nowarn", str(PATCH_OFFLINE)], cwd=dest, check=True)
    if extra_patch is not None:
        subprocess.run(["git", "apply", "--whitespace=nowarn", str(extra_patch)], cwd=dest, check=True)
    return dest


def ensure_host_dist(src: Path) -> None:
    dist = src / "apps" / "host" / "dist" / "index.html"
    if dist.is_file():
        return
    host = src / "apps" / "host"
    subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=host, check=True)
    subprocess.run(["npx", "vite", "build"], cwd=host, check=True)
    if not dist.is_file():
        raise SystemExit("host build did not write dist/index.html")


def extract_llama(payload: Path) -> None:
    stage = WORK / "llama-extract"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    with zipfile.ZipFile(fetch("llama.zip")) as archive:
        archive.extractall(stage)
    tops = [item for item in stage.iterdir() if item.is_dir()]
    if len(tops) != 1:
        raise SystemExit(f"llama.cpp zip layout: {tops}")
    dest = payload / "third_party" / "llama.cpp"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(tops[0]), str(dest))


def extract_engines(payload: Path, mapping: dict[str, str]) -> None:
    for archive_name, folder_name in mapping.items():
        dest = payload / "components" / "engine" / folder_name
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        with tarfile.open(fetch(archive_name)) as archive:
            archive.extractall(dest)
        if not (dest / "engine-component.json").is_file():
            raise SystemExit(f"{archive_name} has no engine-component.json")


def overlay_control(payload: Path, src: Path, *, linux: bool) -> None:
    control = payload / "control"
    for name in ("strata.py", "setup.py"):
        shutil.copy2(src / name, control / name)
    for name in ("strata_cli", "strata_control", "serve"):
        copy_tree(src / name, control / name)
    tools = control / "tools"
    tools.mkdir(exist_ok=True)
    shutil.copy2(src / "tools" / "mtp_fetch.py", tools / "mtp_fetch.py")
    if linux:
        shutil.copy2(src / "tools" / "strata_mcp.py", tools / "strata_mcp.py")
    packaged = control / "packaging"
    packaged.mkdir(exist_ok=True)
    shutil.copy2(src / "packaging" / "binary_deps.py", packaged / "binary_deps.py")
    if not (packaged / "binary_deps.py").is_file():
        raise SystemExit("control/packaging/binary_deps.py was not staged")


def stage_host(payload: Path, src: Path) -> None:
    host = payload / "host"
    copy_tree(src / "apps" / "host" / "server", host / "server")
    copy_tree(src / "apps" / "host" / "dist", host / "dist")
    if not (host / "dist" / "index.html").is_file():
        raise SystemExit("host/dist/index.html is missing")


def extract_node_linux(payload: Path) -> None:
    dest = payload / "node"
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fetch("node-linux.tar.gz")) as archive:
        member = next(item for item in archive.getmembers() if item.name.endswith("/bin/node") and item.isfile())
        data = archive.extractfile(member)
        if data is None:
            raise SystemExit("linux node tarball has no bin/node")
        target = dest / "node"
        target.write_bytes(data.read())
        target.chmod(target.stat().st_mode | stat.S_IEXEC)


def copy_drafts(data: Path, src: Path, mtp_rt: Path | None) -> None:
    """DFlash2 tuned packs, draft vocabularies, and the prepared MTP runtime when it exists."""
    folder = data / "dflash2"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fetch("dflash-selq4.pack"), folder / "qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack")
    shutil.copy2(fetch("dflash-bf16sel.pack"), folder / "qwen3.8-flash-next-dflash2.strata1.q4_0-bf16sel.pack")
    notice = src / "data" / "dflash2-tuned"
    if (notice / "LICENSE").is_file():
        shutil.copy2(notice / "LICENSE", folder / "LICENSE-dflash2-tuned")
    if (notice / "NOTICE.md").is_file():
        shutil.copy2(notice / "NOTICE.md", folder / "NOTICE-dflash2-tuned.md")
    vocab_names = ("draft_vocab.bin", "draft_vocab_en.bin", "draft_vocab_cyrillic.bin", "draft_vocab_fr.bin")
    for name in vocab_names:
        src_file = src / "data" / name
        if src_file.is_file():
            shutil.copy2(src_file, folder / name)
    extra = Path(os.environ.get("STRATA_DFLASH_EXTRA", "/tmp/dflash-extra"))
    # The stock pack is what sets without a tuned entry use. It is built on this machine from the
    # pinned safetensors file and kept only when it matches the hash in strata_control/drafting.py.
    known = {
        "qwen3.8-flash-next-dflash2.q4_0.pack": "cda40d62d0eb8f37ed6e272142641a1d2f0de4a32f9e14d0416e7a71534849f1",
        "qwen3.8-flash-next-dflash2.q4_0-selq4.pack": "4a42b98220ea7880664002c8edda1563aecbae754b762a2e2f31b2b91ee93ecd",
    }
    if extra.is_dir():
        for name, want in known.items():
            path = extra / name
            if path.is_file() and sha256(path) == want:
                shutil.copy2(path, folder / name)
                print(f"included {name}", flush=True)
            elif path.is_file():
                print(f"skipped {name}: hash {sha256(path)} != {want}", flush=True)
    if mtp_rt is None or not (mtp_rt / "experts.bin").is_file():
        (data / "mtp-MISSING.txt").write_text(
            "The prepared MTP runtime (data/mtp/rt/experts.bin) was not available when this archive was built.\n"
            "DFlash2 packs in data/dflash2 are present. Choosing MTP needs the runtime files.\n",
            encoding="utf-8")
        return
    rt = data / "mtp" / "rt"
    if rt.exists():
        shutil.rmtree(rt)
    shutil.copytree(mtp_rt, rt)
    for name in vocab_names:
        src_file = src / "data" / name
        if src_file.is_file() and not (rt / name).is_file():
            shutil.copy2(src_file, rt / name)


def write_common_notes(payload: Path, text: str, build: str) -> None:
    (payload / "使用说明.txt").write_text(text, encoding="utf-8")
    (payload / "OFFLINE_BUILD.txt").write_text(build, encoding="utf-8")


def windows_note() -> str:
    return textwrap.dedent("""
        Strata 0.2.13 离线安装包（Windows 10/11 x64，NVIDIA CUDA 12 与 CUDA 13）

        应用页面来自上游 Niko1221/Strata 标签 v0.2.13（提交 d2f096475）。
        打进包里的 Windows Control 是发布文件 strata-control-0.1.59-windows-x86_64.zip：
        VERSION 文件是 0.1.59，Terminal 的产品版本字符串是 0.2.13，提交 d2f096475。
        两套引擎都是该发布里的 0.1.59。清单里的 notes 仍写着 “0.2.9 NVIDIA”，那是上游文件里的原文。
        上游说明里的「Windows Terminal 仍是 0.2.12」指的是：在已经装了 0.2.12 的电脑上执行
        strata update 时，v0.2.13 的更新源没有 Windows Control，所以 Terminal 留在 0.2.12，只升级引擎。
        本包是一份新的安装，Terminal 产品版本是 0.2.13，不是把 0.2.12 改个号码。

        引擎目录分开，不会把两套 DLL 放进同一个搜索路径：
        - CUDA 12.9：components\\engine\\0.1.59-windows-x86_64-cuda-cuda12
          显卡代码 sm_60、sm_61、sm_70、sm_75、sm_80、sm_86、sm_89（另有 compute_89 的 PTX）
          驱动门槛 NVIDIA 576.02
        - CUDA 13.0：components\\engine\\0.1.59-windows-x86_64-cuda-cuda13
          显卡代码 sm_75、sm_86、sm_89、sm_120（另有 compute_120 的 PTX）
          驱动门槛 NVIDIA 580.65

        读到显卡代码并且两套都符合时用 CUDA 13。达不到 CUDA 13 时用 CUDA 12。
        没有读到计算能力时不猜 CUDA 13，改用仍包含较旧显卡代码的 CUDA 12。
        手动指定：Start-Strata.cmd --cuda 13 或 --cuda 12。不符合清单就退出。
        电脑里装了 CUDA Toolkit 不会被当成驱动已经达标，它的目录也不会留在 PATH 里。

        这是 0.2.13 的 offline-r1。0.2.11 的 r1 第一次启动会报 No module named binary_deps。
        这里沿用 r2 的放法：control\\packaging\\binary_deps.py 和启动程序放在一起。

        没有网也能安装和第一次打开。不安装 WebView2、Python、Node、VC++ 或 CUDA Toolkit。
        用这台电脑上已经有的浏览器打开窗口里打印的 http://127.0.0.1:8791/ 。
        模型权重不在这个包里。页面里选择已经下好的 GGUF，或 Start-Strata.cmd --model 指向那个文件或文件夹。
        本包装进的准备只处理 qwen4exp（Qwen3.8-Flash-Next）。DeepSeek 引擎不在这个包里。

        草稿：DFlash2 的两个 tuned pack 和准备好的 MTP 运行时在单独的 drafts 压缩包里，
        解压到本目录的 data\\ 下（与 Start-Strata.cmd 同级出现 data\\dflash2 和 data\\mtp）。
        若那些文件不在，启动不会下载它们：DFlash2 保持未安装，选择 MTP 时准备步骤会停下并说明缺文件。

        页面里的 Drafting 可以选择 Auto、MTP、DFlash2 或 Off。
        终端里同一份运行配置的 drafting 字段用这四个词。确认生效时看引擎启动参数：
        DFlash2 含 --draft dflash2 和 --draft-model，并且指向 data\\dflash2 里的 pack；
        MTP 含 --mtp，并且指向 data\\mtp\\rt。

        显卡驱动是唯一需要目标系统自己具备的 GPU 组件。没有 NVIDIA 驱动时，程序只报告缺驱动并退出。
    """).strip() + "\n"


def linux_note() -> str:
    return textwrap.dedent("""
        Strata 0.2.13 离线便携包（Linux x86_64）

        应用页面来自上游标签 v0.2.13（提交 d2f096475）。
        Control 用的是发布文件 strata-control-0.1.59.1-linux-x86_64.tar.gz，再叠上离线入口。
        这就是 v0.2.13 发布说明里的 0.2.13.1：Linux 桌面在 Intel Arc 上准备模型时不再停在
        “no NVIDIA GPU found”。VERSION 是 0.1.59.1，Terminal 产品版本字符串是 0.2.13.1。
        引擎仍是 0.1.59，没有 0.1.59.1 的引擎包。

        三套引擎目录分开：
        - CUDA 12.9：components/engine/0.1.59-linux-x86_64-cuda-cuda12
          显卡代码 sm_60 到 sm_89，另有 compute_89。驱动门槛 NVIDIA 575.51。
        - CUDA 13.0：components/engine/0.1.59-linux-x86_64-cuda-cuda13
          显卡代码 sm_75、sm_86、sm_89、sm_120，另有 compute_120。驱动门槛 NVIDIA 580.65。
        - SYCL（Intel Arc）：components/engine/0.1.59-linux-x86_64-sycl
          没有 NVIDIA 驱动时自动用这一套。Start-Strata.sh --cuda sycl 可以指定。

        读到 NVIDIA 显卡代码并且两套 CUDA 都符合时用 CUDA 13。没有读到计算能力时不猜 CUDA 13。
        没有 NVIDIA、并且本包有 SYCL 引擎时，用 SYCL，不要求先装 NVIDIA 驱动。
        AMD HIP 引擎不在这个包里。

        解压后执行 ./Start-Strata.sh。用已经装在这台电脑上的浏览器打开它打印的
        http://127.0.0.1:8791/ 。不安装系统 Python、Node 或 CUDA Toolkit。
        模型权重不在包里。--model 指向本机 GGUF 文件或文件夹。
        准备只处理 qwen4exp。DeepSeek 引擎不在这个包里。

        DFlash2 的两个 tuned pack（selq4 约 0.32 GiB，bf16sel 约 0.49 GiB）在 data/dflash2/。
        准备好的 MTP 运行时在 data/mtp/rt/（experts.bin、dense.bin、dense.txt 和 draft_vocab.bin）。
        这些文件随本便携包一起提供，第一次启动不会再下载它们。
        缺文件时不会联网去补：DFlash2 保持未安装；选择 MTP 而 experts.bin 不在时，准备步骤停下并说明缺什么。

        页面 Drafting：Auto、MTP、DFlash2、Off。
        生效时引擎参数里能看到 --draft dflash2 --draft-model <data/dflash2 里的 pack>，
        或 --mtp <data/mtp/rt>。Auto 在这块卡的默认是 DFlash2 时用 selq4（引擎能读 Q4_0 selector 时）
        或 bf16sel（SYCL 引擎读 bf16 selector）。卡片不适合 DFlash2 时 Auto 用 MTP。

        显卡驱动要系统自己有：NVIDIA 驱动，或 Intel GPU 的 Level Zero 驱动。本包不安装驱动。
    """).strip() + "\n"


def start_cmd() -> str:
    return textwrap.dedent(r"""
        @echo off
        setlocal
        cd /d "%~dp0"
        if not exist "%~dp0data\dflash2\qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack" (
          echo DFlash2 pack is not in data\dflash2. Extract the drafts archive here before the first start if you need drafting offline.
          echo Drafting stays off until those files are present. Nothing will be downloaded.
        )
        "%~dp0control\python\python.exe" "%~dp0control\strata.py" offline --root "%~dp0." %*
        if errorlevel 1 (
          echo.
          echo Strata did not start. The message above names what is missing.
          pause
        )
    """).lstrip().replace("\n", "\r\n")


def start_sh() -> str:
    return textwrap.dedent("""
        #!/bin/sh
        set -eu
        cd "$(dirname "$0")"
        ROOT=$(pwd)
        if [ ! -f "$ROOT/data/dflash2/qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack" ]; then
          echo "DFlash2 pack is not in data/dflash2. Drafting stays unavailable. Nothing will be downloaded."
        fi
        exec "$ROOT/control/python/bin/python3" "$ROOT/control/strata.py" offline --root "$ROOT" "$@"
    """).lstrip()


def build_record(kind: str) -> str:
    lines = [
        f"offline-v0.2.13-r1 {kind}",
        f"upstream tag {TAG} commit {TAG_COMMIT}",
        "app host built from that tag plus the offline entry",
        "node 24.12.0",
        "llama.cpp 3cf03257f219afbe7334045ff7c6a06ac68c627d",
        "serve/server.py is the patched checkout, not the untouched copy from the control archive",
        "control/packaging/binary_deps.py is installed (the 0.2.11 r2 fix)",
        "model weights are not included",
    ]
    if kind == "windows":
        lines += [
            "control strata-control-0.1.59-windows-x86_64.zip VERSION 0.1.59 PRODUCT_VERSION 0.2.13",
            "control commit recorded in that zip: d2f096475817d4666c364c820b0ca830f751cfc5",
            "engine cuda12 0.1.59 sha256 934ac7f321e89a8935c26037ff32fcc0acce526e492c544b98aaf5dec86dbe46 driver 576.02",
            "engine cuda13 0.1.59 sha256 3f071a7ccbbf3dcdefed8bff777896d8dd0b580417a078154a7d2c2402ec4158 driver 580.65",
            "Windows feed has no Control update: an existing 0.2.12 Terminal stays 0.2.12 on strata update. This package is a new tree and its product string is 0.2.13.",
            "DFlash2 and MTP files are the separate drafts archive, extracted into data\\",
        ]
    else:
        lines += [
            "control strata-control-0.1.59.1-linux-x86_64.tar.gz VERSION 0.1.59.1 PRODUCT_VERSION 0.2.13.1",
            "that archive's COMMIT is 628f74955a56fcba092495b800dd02af75373a0f; the Arc setup fix is commit 1130d824 and the version bump is b08a069d",
            "engine cuda12 0.1.59 sha256 4bf321cb0c2d7ff15fe221f22a29aeb8371f24fa77a4425c920eb01a520babbc driver 575.51",
            "engine cuda13 0.1.59 sha256 42ab04fa3201e41bef5fac28c05f5c35c909419ec937d879b505bf1516742610 driver 580.65",
            "engine sycl 0.1.59 sha256 8b2586ab57a2ad8df593d11dc6a3509620ca49fb352692ae0f7f4f7d014a7839",
            "DFlash2 packs and the prepared MTP runtime are in data/",
        ]
    return "\n".join(lines) + "\n"


def preflight(payload: Path, src: Path) -> None:
    # A second payload must not keep the first tree's already-imported modules.
    for name in list(sys.modules):
        if name == "binary_deps" or name == "node_runtime" or name == "strata_control" or name.startswith("strata_control."):
            del sys.modules[name]
    sys.path.insert(0, str(src))
    sys.path.insert(0, str(src / "packaging"))
    from strata_control.windows_offline import preflight as check
    report = check(payload)
    if not report.ok:
        for issue in report.issues:
            print(issue.line(), file=sys.stderr)
        raise SystemExit(f"preflight failed for {payload}")
    import binary_deps
    for folder in (payload / "components" / "engine").iterdir():
        bad = binary_deps.uncovered(folder)
        if bad:
            raise SystemExit(f"{folder.name} import closure is open: {bad[:8]}")
    node_bad = binary_deps.uncovered(payload / "node")
    if node_bad:
        raise SystemExit(f"node import closure is open: {node_bad[:8]}")


def product_version(control: Path) -> str:
    text = (control / "strata_cli" / "__init__.py").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("PRODUCT_VERSION"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("PRODUCT_VERSION missing")


def nsis(payload: Path, outfile: Path) -> None:
    nsi = WORK / "offline.nsi"
    nsi.write_text(textwrap.dedent(f"""
        Unicode true
        SetCompressor zlib
        RequestExecutionLevel user
        Name "Strata 0.2.13 Offline"
        OutFile "{outfile.as_posix()}"
        InstallDir "$LOCALAPPDATA\\StrataOffline"
        ShowInstDetails show
        Section
          SetOutPath "$INSTDIR"
          File /r "{payload.as_posix()}/*"
          CreateShortcut "$DESKTOP\\Strata Offline.lnk" "$INSTDIR\\Start-Strata.cmd"
        SectionEnd
    """).lstrip(), encoding="utf-8")
    subprocess.run(["makensis", "-NOCD", str(nsi)], check=True)


def split_file(path: Path, dest_dir: Path) -> list[Path]:
    if path.stat().st_size <= PART:
        target = dest_dir / path.name
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
        return [target]
    prefix = dest_dir / (path.name + ".part-")
    subprocess.run(["split", "-b", str(PART), "-d", "-a", "2", str(path), str(prefix)], check=True)
    parts = sorted(dest_dir.glob(path.name + ".part-*"))
    total = sum(item.stat().st_size for item in parts)
    if total != path.stat().st_size:
        raise SystemExit(f"parts of {path.name} sum {total} != {path.stat().st_size}")
    return parts


def checksum_lines(paths: list[Path]) -> str:
    lines = []
    for path in paths:
        lines.append(f"{sha256(path)}  {path.name}  {path.stat().st_size}")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not PATCH_OFFLINE.is_file() or not PATCH_LINUX.is_file():
        raise SystemExit("patches are missing")
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    windows_src = prepare_source("STRATA_SRC", WORK / "src-windows", None)
    linux_src = prepare_source("STRATA_LINUX_SRC", WORK / "src-linux", PATCH_LINUX)
    ensure_host_dist(windows_src)
    mtp_rt = Path(os.environ.get("STRATA_MTP_RT", "/tmp/mtp-rt"))
    if not (mtp_rt / "experts.bin").is_file():
        print(f"MTP runtime not at {mtp_rt}; drafts will record it as missing", flush=True)
        mtp_rt = None

    # Windows payload. Drafters stay out of the NSIS installer so the exe stays under 2 GiB.
    win = WORK / "windows-payload"
    if win.exists():
        shutil.rmtree(win)
    win.mkdir(parents=True)
    sys.path.insert(0, str(windows_src / "packaging"))
    import node_runtime
    node_runtime.extract(fetch("node-win.zip"), win / "node")
    with zipfile.ZipFile(fetch("control-win.zip")) as archive:
        archive.extractall(win / "control")
    overlay_control(win, windows_src, linux=False)
    extract_engines(win, WIN_ENGINES)
    extract_llama(win)
    stage_host(win, windows_src)
    (win / "Start-Strata.cmd").write_bytes(start_cmd().encode("utf-8"))
    if product_version(win / "control") != "0.2.13":
        raise SystemExit("windows PRODUCT_VERSION is not 0.2.13")
    version_text = (win / "control" / "VERSION").read_text(encoding="utf-8").strip()
    if version_text != "0.1.59":
        raise SystemExit(f"windows VERSION file is {version_text}, expected 0.1.59")
    write_common_notes(win, windows_note(), build_record("windows"))
    preflight(win, windows_src)
    exe = WORK / "Strata-0.2.13-offline-r1-windows-x64-cuda12-cuda13-setup.exe"
    if exe.exists():
        exe.unlink()
    print("makensis", flush=True)
    nsis(win, exe)

    # Drafts archive, shared instructions for the Windows install directory.
    drafts = WORK / "drafts-root" / "data"
    if drafts.exists():
        shutil.rmtree(drafts.parent)
    copy_drafts(drafts, windows_src, mtp_rt)
    drafts_tar = WORK / "Strata-0.2.13-offline-r1-drafts.tar"
    if drafts_tar.exists():
        drafts_tar.unlink()
    with tarfile.open(drafts_tar, "w") as archive:
        archive.add(drafts.parent / "data", arcname="data")

    # Linux portable, drafts included.
    lin = WORK / "linux-root" / "Strata-0.2.13-offline-r1-linux-x86_64"
    if lin.exists():
        shutil.rmtree(lin.parent)
    lin.mkdir(parents=True)
    extract_node_linux(lin)
    with tarfile.open(fetch("control-linux.tar.gz")) as archive:
        archive.extractall(lin / "control")
    overlay_control(lin, linux_src, linux=True)
    extract_engines(lin, LINUX_ENGINES)
    extract_llama(lin)
    stage_host(lin, windows_src)
    script = lin / "Start-Strata.sh"
    script.write_text(start_sh(), encoding="utf-8")
    script.chmod(0o755)
    if product_version(lin / "control") != "0.2.13.1":
        raise SystemExit("linux PRODUCT_VERSION is not 0.2.13.1")
    version_text = (lin / "control" / "VERSION").read_text(encoding="utf-8").strip()
    if version_text != "0.1.59.1":
        raise SystemExit(f"linux VERSION file is {version_text}, expected 0.1.59.1")
    copy_drafts(lin / "data", linux_src, mtp_rt)
    write_common_notes(lin, linux_note(), build_record("linux"))
    preflight(lin, linux_src)
    linux_tar = WORK / "Strata-0.2.13-offline-r1-linux-x86_64-portable.tar"
    if linux_tar.exists():
        linux_tar.unlink()
    print("tar linux", flush=True)
    with tarfile.open(linux_tar, "w") as archive:
        archive.add(lin, arcname=lin.name)

    produced = [exe, drafts_tar, linux_tar]
    shipped: list[Path] = []
    for item in produced:
        shipped.extend(split_file(item, OUT))
    whole = []
    for item in produced:
        whole.append(f"{sha256(item)}  {item.name}  {item.stat().st_size}")
    listing = "\n".join(whole) + "\n\n# upload pieces (a file at or under 1900 MiB is stored whole)\n" + checksum_lines(shipped)
    (OUT / "SHA256SUMS.txt").write_text(listing, encoding="utf-8")
    print(listing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
