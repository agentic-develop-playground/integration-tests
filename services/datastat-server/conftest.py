# -*- coding: utf-8 -*-
"""
项目级 pytest 配置：默认以「有头模式」运行 Playwright 浏览器。

覆盖 pytest-playwright 提供的 fixture：
- browser_type_launch_args: 设置 headless=False，让浏览器窗口可见
- 同时放慢 50ms slow_mo，便于肉眼观察操作过程

如需切回无头模式，命令行追加：--headed=false 或 设环境变量 HEADLESS=1
"""

import os

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """以有头模式启动浏览器（除非显式设 HEADLESS=1）"""
    headless = os.environ.get("HEADLESS", "0") == "1"
    return {
        **browser_type_launch_args,
        "headless": headless,
        "slow_mo": int(os.environ.get("SLOW_MO", "50")),
    }
