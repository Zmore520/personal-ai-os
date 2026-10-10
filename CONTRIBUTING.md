# Contributing

Use Python 3.10+ and run:

```sh
python -m unittest discover -s tests -v
python -m paos validate examples/exchange
python tools/check_public.py
```

Keep examples synthetic, runtime dependencies minimal, and English/Chinese capability tables consistent. Include meaningful regression tests for state transitions, provenance checks and conflict behavior. Explain which capability you actually verified and which remains hypothetical.

Never commit real operating data, credentials or private conversation excerpts. Do not add an execution adapter without an explicit authorization model, transactional claim/effect design and documented revocation. The repository is not a place to post another person's private agent output.

中文：贡献需使用合成数据、运行上述检查，并同步维护中英文能力边界。新增连接器要说明实测结果、认证、撤销、并发和幂等处理，不能把计划当成已实现功能。
