"""支持 `python -m zhuo_agent.cli` 方式启动 CLI。

仅作为薄封装，直接调用 main 模块的 main()，不含其他逻辑。
"""

from zhuo_agent.cli.main import main

main()
