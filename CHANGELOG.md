# Changelog

## [1.0.0](https://github.com/Garulf/pyFlowLauncher/compare/v0.10.0...v1.0.0) (2026-07-09)


### Features

* add api.fuzzy_search() with V2 host call and V1 local fallback ([d01b62e](https://github.com/Garulf/pyFlowLauncher/commit/d01b62ed93922aad37f8225c970f558122d2c39f))
* add Launcher class with V1/V2 protocol support ([4cb8686](https://github.com/Garulf/pyFlowLauncher/commit/4cb8686c1b79be6e90c209021f26dd68a75b40c8))
* add Launcher class with V1/V2 protocol support and DI into Plugin ([6adff26](https://github.com/Garulf/pyFlowLauncher/commit/6adff2692d3d69673d5c65e07cd014e08a17be5f))


### Bug Fixes

* add from __future__ import annotations to response.py for Python 3.8 compat ([2b28a5b](https://github.com/Garulf/pyFlowLauncher/commit/2b28a5bf768dc0b4651697dbf55a15d631a77895))
* address code review findings in Launcher implementation ([db188b4](https://github.com/Garulf/pyFlowLauncher/commit/db188b466239bb8e60653172fd0a6b95a6eba5e4))
* address code review findings in V2 protocol and launcher ([c50a56d](https://github.com/Garulf/pyFlowLauncher/commit/c50a56d3f7da256522ede59ac6f48b61548731cf))
* correct V2 protocol request parsing and response format ([ce01c8a](https://github.com/Garulf/pyFlowLauncher/commit/ce01c8a022bade1986d43afad30f2410fe357607))
* **lint:** remove unused asyncio and sys imports from launcher.py ([469e505](https://github.com/Garulf/pyFlowLauncher/commit/469e505a45542f9c70661017957f87234902a5cb))
* **lint:** wrap long line in exception handler response ([da00d55](https://github.com/Garulf/pyFlowLauncher/commit/da00d556e729d270d6de5520c91ec58380a66b9d))
* **tests:** add __future__ annotations for Python 3.8/3.9 compat ([2f4521d](https://github.com/Garulf/pyFlowLauncher/commit/2f4521da65930b5cbed5d7d4aa8154f2f588fd42))
* **tests:** make unmatched-id log test work on pytest &lt; 9 ([a29f645](https://github.com/Garulf/pyFlowLauncher/commit/a29f645b592fb91b376415ead886c76575ff4453))


### Miscellaneous Chores

* release 1.0.0 ([76736e1](https://github.com/Garulf/pyFlowLauncher/commit/76736e1c8b2c77cac035eb0ba73a92b9fa9b71e0))
