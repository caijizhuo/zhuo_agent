"""`zhuo --version` 子命令：打印当前安装的包版本号。

从包顶层读取 __version__ 并输出，不做其他处理。
"""

import zhuo_agent


# 打印当前 zhuo_agent 包的版本号
def cmd_version() -> None:
    print(zhuo_agent.__version__)
