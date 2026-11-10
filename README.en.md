# Strata full offline installer for Windows

[中文](README.md)

This is a complete offline Windows installer built from an official Strata release. Installing it and opening it the first time does not need a network. The upstream version for each package is in that Release's notes.

## Download

Get the files from [Releases](https://github.com/Family2002/full-offline-strata-qwen/releases).

Each release has two pieces:

- The installer: one `.exe`.
- The drafter archive: `drafts.tar`. When it is too large it is split into `drafts.tar.part-00`, `part-01`, and so on. Join those pieces first.

Checksums are in `SHA256SUMS.txt` on that Release.

## Join the pieces and check them

Put the pieces in one folder, join them, then check the hash. In `SHA256SUMS.txt`, the first line for a name is the joined file.

```sh
cat Strata-*-drafts.tar.part-* > Strata-drafts.tar
sh packaging/reassemble.sh Strata-drafts.tar
```

`reassemble.sh` checks the joined file against `SHA256SUMS.txt`. On Windows you can copy the pieces together in name order and compare the hash before opening the archive.

## Offline install and first start

1. Run the installer. It installs to `%LOCALAPPDATA%\StrataOffline`. It does not ask for an administrator and it does not use the network.
2. Extract the joined `drafts.tar` into that folder so these two directories exist:
   - `%LOCALAPPDATA%\StrataOffline\data\dflash2`
   - `%LOCALAPPDATA%\StrataOffline\data\mtp`
3. Run `%LOCALAPPDATA%\StrataOffline\Start-Strata.cmd`.
4. Open the address it prints in a browser already on the PC.
5. Choose a model that is already on the PC, or start with `--model` pointing at that file or folder.

The installer does not add Python, Node, or a graphics driver. If a file that belongs in the package is missing, the program names it and exits. It does not download a replacement. Model weights are not in the installer; bring your own. The graphics driver and the browser are the ones already on the PC.

## Turn on MTP and DFlash2

Do step 2 above first, so `drafts.tar` is extracted into the install folder. Without that, drafting does not turn on, and the program will not fetch the missing files.

In the page, open **Drafting** and choose:

- **Auto**: let this PC pick.
- **MTP** or **DFlash2**: use that one.
- **Off**: leave drafting off.

After you load a model, the drafting note on the page says which one is in use. If you chose MTP or DFlash2 and the note says a file is still missing, `drafts.tar` was not extracted into the install folder, or it was extracted somewhere else.

## Limits

- Windows only.
- You supply the model weights.
- Drafters are a separate archive. Join the pieces when it was split.
- There is no uninstaller. Delete `%LOCALAPPDATA%\StrataOffline`, then delete the desktop shortcut.
- The installer has not been run through inference on every graphics card.
