# Strata Windows 完整离线安装包

[English](README.en.md)

这是基于 Strata 正式版打好的 Windows 完整离线安装包。安装和第一次打开不需要联网。每个包对应的上游版本写在该 Release 的说明里。

## 下载

到 [Releases](https://github.com/Family2002/full-offline-strata-qwen/releases) 页面下载。

每个版本有两样东西：

- 安装包：一个 `.exe`。
- 草稿模型包：`drafts.tar`。文件太大时会分成 `drafts.tar.part-00`、`part-01` 等，需要先拼回。

校验和在该 Release 的 `SHA256SUMS.txt` 里。

## 拼分卷和校验

把分卷放在同一目录，拼回后核对哈希。`SHA256SUMS.txt` 里同一文件名的第一行是拼回后的整份文件。

```sh
cat Strata-*-drafts.tar.part-* > Strata-drafts.tar
sh packaging/reassemble.sh Strata-drafts.tar
```

`reassemble.sh` 会按 `SHA256SUMS.txt` 检查拼回的文件。Windows 上也可以把分卷按文件名顺序拷成一个文件，再用资源管理器或 7-Zip 打开前先对一下哈希。

## 离线安装与首次启动

1. 运行下载的安装包。它装到 `%LOCALAPPDATA%\StrataOffline`，不需要管理员权限，也不访问网络。
2. 把拼好的 `drafts.tar` 解压到这个目录，使下面两个文件夹出现：
   - `%LOCALAPPDATA%\StrataOffline\data\dflash2`
   - `%LOCALAPPDATA%\StrataOffline\data\mtp`
3. 运行 `%LOCALAPPDATA%\StrataOffline\Start-Strata.cmd`。
4. 用这台电脑上已经有的浏览器，打开窗口里打印的地址。
5. 在页面里选择本机已经准备好的模型，或启动时加上 `--model` 指向那个文件或文件夹。

不会另外安装 Python、Node 或显卡驱动。缺了包里该有的文件时，程序会说明缺什么并退出，不会去下载。模型权重不在安装包里，需要自己放在本机。显卡驱动和浏览器用电脑上现成的。

## 开启 MTP 和 DFlash2

先完成上面第 2 步，把 `drafts.tar` 解进安装目录。没有这一步，草稿不会生效，程序也不会联网去补。

在页面的 **Drafting** 里选择：

- **Auto**：按这台电脑自动选。
- **MTP** 或 **DFlash2**：固定用这一种。
- **Off**：关闭草稿。

选好并加载模型之后，页面上的草稿说明会写当前用的是哪一种。如果选了 MTP 或 DFlash2，说明却提示还缺文件，就是 `drafts.tar` 没解到安装目录，或解错了位置。

## 已知限制

- 只提供 Windows 安装包。
- 模型权重需要自己准备。
- 草稿是单独的压缩包；太大时要先拼分卷。
- 没有卸载程序。删掉 `%LOCALAPPDATA%\StrataOffline`，再删掉桌面上的快捷方式即可。
- 安装包没有在每一张显卡上跑过推理。
