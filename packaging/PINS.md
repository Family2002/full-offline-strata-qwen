# Pinned upstream files for the v0.2.13 offline packages

Every archive below is downloaded by `packaging/build_offline_release.py` and refused when the SHA-256 differs. The hashes are the ones published with [Niko1221/Strata v0.2.13](https://github.com/Niko1221/Strata/releases/tag/v0.2.13) (`SHA256SUMS.txt`) and with the Node 24.12.0 and llama.cpp pins named by that tag's `fetch-node.sh` and `setup.py`.

| File | SHA-256 |
| --- | --- |
| `node-v24.12.0-win-x64.zip` | `9c125f61ae947b52e779095830f9cac267846a043ef7192183c84016aaad2812` |
| `node-v24.12.0-linux-x64.tar.gz` | `6159227e0af7d7c3c6bb2fa900452b04a6cb8841a702a79acc613209d70b04d0` |
| llama.cpp `3cf03257f219afbe7334045ff7c6a06ac68c627d` | `cbe23c594282ead2937abb3f008e51fcec4609d9256652fff42c7cc1c21ea47b` |
| `strata-control-0.1.59-windows-x86_64.zip` | `c81f6800094942a5e750c7d93f348062bc16484f946ea83b0c0d2f8c91c44e87` |
| `strata-control-0.1.59.1-linux-x86_64.tar.gz` | `73fb612848cf00fa1072623029b35405bbbb63e3f4c688fe6f38c78e3fc022ac` |
| `strata-engine-0.1.59-windows-x86_64-cuda-cuda12.tar.gz` | `934ac7f321e89a8935c26037ff32fcc0acce526e492c544b98aaf5dec86dbe46` |
| `strata-engine-0.1.59-windows-x86_64-cuda-cuda13.tar.gz` | `3f071a7ccbbf3dcdefed8bff777896d8dd0b580417a078154a7d2c2402ec4158` |
| `strata-engine-0.1.59-linux-x86_64-cuda-cuda12.tar.gz` | `4bf321cb0c2d7ff15fe221f22a29aeb8371f24fa77a4425c920eb01a520babbc` |
| `strata-engine-0.1.59-linux-x86_64-cuda-cuda13.tar.gz` | `42ab04fa3201e41bef5fac28c05f5c35c909419ec937d879b505bf1516742610` |
| `strata-engine-0.1.59-linux-x86_64-sycl.tar.gz` | `8b2586ab57a2ad8df593d11dc6a3509620ca49fb352692ae0f7f4f7d014a7839` |
| `qwen3.8-flash-next-dflash2.strata1.q4_0-selq4.pack` | `4df2e5ab2b47c064afbe662e16e4f06569877125c2d0e2123a4ac755266c664c` |
| `qwen3.8-flash-next-dflash2.strata1.q4_0-bf16sel.pack` | `34ca17fee701ff088b6069acc35a26661d237953f5d114be0a3f7dae3ec5cda9` |

The stock DFlash2 pack is not a release file. Upstream builds it locally from `incoai/Qwen3.8-Flash-Next-DFlash2` revision `a22a1744e85c17364dcc54a6a420af7135d4c7f6` (`model.safetensors` SHA-256 `d6723f2a359eaf33ec0c95f22ae8edda896774020c552296a85e1913b4d3186f`). The resulting `qwen3.8-flash-next-dflash2.q4_0.pack` must be SHA-256 `cda40d62d0eb8f37ed6e272142641a1d2f0de4a32f9e14d0416e7a71534849f1`. The selector conversion of that pack must be SHA-256 `4a42b98220ea7880664002c8edda1563aecbae754b762a2e2f31b2b91ee93ecd`. A file that does not match is not shipped.

MTP tensors are read from `Qwen/Qwen3.8-Flash-Next` revision `de4b8e4d43b917e7706784d8bb445c9af86a3540` by `tools/mtp_fetch.py`, then packed with `tools/mtp_pack.py --experts q2_0` and `tools/mtp_rt.py`. The runtime that is shipped is `data/mtp/rt/` (`experts.bin`, `dense.bin`, `dense.txt`), not the 5 GB of raw tensors.
