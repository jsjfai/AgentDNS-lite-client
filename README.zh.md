<p align='center'>
<img src='./resources/icon.png' width="150" height="150" alt="AgentDNS Icon" />
</p>

# agentdns-lite-client

本工程是一个基于 **MCP 协议** 的智能体网络客户端，结合了 **gentDNS** 与 **大模型**，实现了以下功能：

- 🔍 将用户输入的自然语言问题 **自动拆分为子任务**
- 📂 使用 **规则 + AgentDNS 提供的 categories** 进行任务分类
- 🌐 调用 **AgentDNS** 获取对应的智能服务入口 (Smart 服务 baseurl)
- ⚙️ 通过 **Smart 服务** 的工具（`get_available_tools` / `execute_tool`）执行任务
- 🤖 当分类失败（`unknown`）时，自动回退到 **大模型** 直接回答
- 🌐 **多语言支持**：支持中文和英文界面切换

---

## 📂 工程结构
```
agent-cli-client
├── ai_agent_dns.py         # AgentDNS SSE 客户端 (获取 categories / query category)
├── config_loader.py        # 配置文件加载器
├── configure.json          # 配置文件（语言设置 / 大模型 API Key / AgentDNS SSE URL / 分类规则）
├── match.py                # 任务与类别的规则匹配
├── question_classify.py    # 使用大模型将用户问题拆分为子任务
├── task_decompose.py       # 调用工具以获取任务所需的可用工具 (get_available_tools / execute_tool)
├── i18n.py                 # 国际化支持模块
├── resources/              # 资源文件目录
│   ├── banner_zh_CN.txt    # 中文启动横幅
│   ├── banner_en_US.txt    # 英文启动横幅
│   └── i18n/               # 国际化配置文件
│       ├── zh-CN.json      # 中文语言包
│       └── en-US.json      # 英文语言包
├── README.md               # 项目说明
└── start_aiagentdns_loop_threads.py          # 主入口：完整流程 (分类 → 匹配 → Smart 调用 → 大模型兜底)
```

安装依赖：
``` bash
pip install -r requirements.txt
```

## 📑 配置文件
请编辑 configure.json：
``` json
{
  "language": "zh-CN",                        // 界面语言：zh-CN (中文) 或 en-US (英文)
  "deepseek": {
    "api_key": "sk-xxxxxxx",                  // 你的大模型 API Key
    "base_url": "https://api.deepseek.com/v1" // 大模型 base URL
  },
  "agentdns": {
    "sse_url": "https://aitest.jsjfsz.com:8300/agentdns/main/sse"   // AgentDNS SSE 服务地址
  },
  "category_rules": {
    "weather_forecast": ["天气", "weather", "气温", "湿度", "风力"],
    "maps_location": ["餐馆", "地图", "位置", "附近", "饭店", "地铁", "map"],
    "video_search": ["视频", "b站", "抖音", "youtube", "video", "影片"]
  }
}
```

## 🌐 多语言支持

### 方式一：配置文件设置
在 `configure.json` 中设置 `language` 字段：
- `"zh-CN"`: 中文界面
- `"en-US"`: 英文界面

### 方式二：环境变量设置
```bash
# 使用英文界面
export AGENTDNS_LANG=en-US
python start_aiagentdns_loop_threads.py

# 使用中文界面
export AGENTDNS_LANG=zh-CN
python start_aiagentdns_loop_threads.py
```

### 支持的语言
- **中文 (zh-CN)**: 默认语言，完整功能支持
- **英文 (en-US)**: 完整功能支持，包含英文启动横幅和界面文本

## ▶️ 运行示例

### 中文界面运行
```bash
python start_aiagentdns_loop_threads.py
```

### 英文界面运行
```bash
# 方式一：修改配置文件 configure.json 中的 "language": "en-US"
python start_aiagentdns_loop_threads.py

# 方式二：使用环境变量
export AGENTDNS_LANG=en-US
python start_aiagentdns_loop_threads.py
```

---
## 📌 功能说明

1. **任务拆分**
   question_classify.py 使用大模型将用户输入拆分成多个编号任务。

2. **分类匹配**
   match.py 根据配置文件中的关键词规则匹配到 AgentDNS 提供的 categories。
   - 匹配到 → 使用 Smart 服务执行
   - 匹配失败 → 使用大模型兜底回答

3. **任务适配服务调用**
   task_decompose.py
   - get_available_tools → 获取候选工具
   - 遍历工具并调用 execute_tool，自动用大模型生成 arguments
   - 先找到能返回结果的工具就停止

4. **兜底机制**
   - 当全部任务都是 unknown 时，直接调用大模型输出结果。
   - 当部分任务 unknown，部分匹配到 → 混合输出（部分任务适配，部分大模型）。

5. **多语言国际化**
   i18n.py 提供完整的国际化支持：
   - 自动根据配置文件或环境变量切换语言
   - 支持动态加载不同语言的界面文本和启动横幅
   - 可扩展的语言包系统，支持自定义添加新语言
