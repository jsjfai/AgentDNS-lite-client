<p align='center'>
<img src='./resources/icon.png' width="150" height="150" alt="AgentDNS Icon" />
</p>

# agentdns-lite-client

# MCP-based Intelligent Agent Network Client

This project is an **MCP protocol–based** intelligent agent network client, integrating **AgentDNS** with the **LLM**, and implements the following functions:

- 🔍 Automatically **decomposes user natural language queries into subtasks**  
- 📂 Classifies tasks using **rules + AgentDNS-provided categories**  
- 🌐 Invokes **AgentDNS** to obtain the corresponding smart service entry (Smart service base URL)  
- ⚙️ Executes tasks through **Smart services** using tools (`get_available_tools` / `execute_tool`)  
- 🤖 Falls back to the **LLM** for direct answers when classification fails (`unknown`)  
- 🌐 **Multilingual support**: allows switching between Chinese and English interfaces  

---

## 📂 Project Structure
```
agent-cli-client
|- ai_agent_dns.py         # AgentDNS SSE client (fetch categories / query category)
|- config_loader.py        # Configuration file loader
|- configure.json          # Configuration (language / LLM API Key / AgentDNS SSE URL / classification rules)
|- match.py                # Rule-based task-category matching
|- question_classify.py    # Use LLM to decompose user query into subtasks
|- task_decompose.py       # Call Smart services (get_available_tools / execute_tool)
|- i18n.py                 # Internationalization module
|- resources/              # Resource files
   |- banner_zh_CN.txt     # Startup banner (Chinese)
   |- banner_en_US.txt     # Startup banner (English)
   |- i18n/                # Language packs
       |- zh-CN.json       # Chinese language pack
       |- en-US.json       # English language pack
|- README.md               # Project documentation (English)
|- README.zh.md            # Project documentation (Chinese)
|- start_aiagentdns_loop_threads.py   # Main entry: full workflow (classify → match → Smart call → LLM fallback)
```

Install dependencies：
``` bash
pip install -r requirements.txt
```

## 📑 config file
edit configure.json：
``` json
{
  "language": "zh-CN",                        // Language：zh-CN or en-US
  "deepseek": {
    "api_key": "sk-xxxxxxx",                  // Your LLM API Key
    "base_url": "https://api.deepseek.com/v1" // LLM base URL
  },
  "agentdns": {
    "sse_url": "https://aitest.jsjfsz.com:8300/agentdns/main/sse"   // AgentDNS SSE service address
  },
  "category_rules": {
    "weather_forecast": ["天气", "weather", "气温", "湿度", "风力"],
    "maps_location": ["餐馆", "地图", "位置", "附近", "饭店", "地铁", "map"],
    "video_search": ["视频", "b站", "抖音", "youtube", "video", "影片"]
  }
}
```

## 🌐 Multilingual Support

### Method 1：config file setting
In `configure.json`, setting `language` field：
- `"zh-CN"`: Chinese
- `"en-US"`: English

### Method 2：environment variable setting
```bash
# Use English interface
export AGENTDNS_LANG=en-US
python start_aiagentdns_loop_threads.py

# Use Chinese interface
export AGENTDNS_LANG=zh-CN
python start_aiagentdns_loop_threads.py
```

### Supported Languages
- **中文 (zh-CN)**: 默认语言，完整功能支持
- **英文 (en-US)**: 完整功能支持，包含英文启动横幅和界面文本

## ▶️ Run examples

### Run with Chinese
```bash
python start_aiagentdns_loop_threads.py
```

### Run with English
```bash
# Method 1: Modify the "language" field in configure.json to "en-US"
python start_aiagentdns_loop_threads.py

# Method 2: Use environment variable
export AGENTDNS_LANG=en-US
python start_aiagentdns_loop_threads.py
```

---
## 📌 Features

1. **Task Decomposition**  
   `question_classify.py` uses **LLM** to split the user’s input into multiple numbered sub-tasks.

2. **Classification & Matching**  
   `match.py` matches tasks to categories provided by **AgentDNS** based on keyword rules in the configuration file.  
   - If matched → execute via **Smart services**  
   - If not matched → fallback to the **LLM** for direct answers

3. **Task-to-Service Adaptation**  
   `task_decompose.py`:  
   - `get_available_tools` → retrieve candidate tools  
   - Iterate through tools and call `execute_tool`, with **LLM** auto-generating arguments  
   - Stop once a tool returns a valid result

4. **Fallback Mechanism**  
   - If **all tasks are unknown**, directly invoke **LLM** for results  
   - If **some tasks are unknown** while others are matched → provide mixed output (partial tool execution + partial LLM response)

5. **Multilingual Support**  
   `i18n.py` provides full internationalization capabilities:  
   - Automatically switches language based on config file or environment variable  
   - Supports dynamic loading of different interface texts and startup banners  
   - Extensible language pack system, allowing easy addition of new languages

