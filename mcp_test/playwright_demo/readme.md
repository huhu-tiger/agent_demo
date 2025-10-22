# 1) 安装依赖

pip install pytest playwright

# 2) 安装浏览器内核（仅首次需要，可选）

python -m playwright install chromium

# 3) 运行该用例

$ pytest -q demo.py::test_baidu_search_mcp --chrome-path "C:\Program Files\Google\Chrome\Application\chrome.exe"


# 4）录制脚本

playwright codegen https://hjytest.jst.huice.cn/huice/api/auth/rest/loginNew -o my_script.py
