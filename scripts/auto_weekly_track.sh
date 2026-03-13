#!/bin/bash
# 自动提取昨日的 Git 提交记录和文档，调用大模型 API 生成总结，更新到 weekly_track.md

# 设定时区为多伦多
export TZ="America/Toronto"

REPO_DIR="/Users/jameshou/Desktop/Repos/dsskillv2"
MD_FILE="$REPO_DIR/proj docs/weekly_track.md"

# ==========================================
# 🚨 用户配置区：请填入您的 API 信息
# ==========================================
# 如果您使用的是 Gemini API，请确保密钥正确，并填写模型名称
export API_KEY="AIzaSyBvBQSOSIPXCUpbmUmJeIfGLhMWJid4he4" 
export MODEL_NAME="gemini-flash-latest" # 使用官方推荐的最新 Flash 别名
# ==========================================

# 昨天的日期
START_TIME=$(date -v-1d +"%Y-%m-%dT01:00:00")
END_TIME=$(date +"%Y-%m-%dT01:00:00")
DAY_NAME=$(date -v-1d +"%A")

case "$DAY_NAME" in
  Sunday) DAY_ZH="周日" ;;
  Monday) DAY_ZH="周一" ;;
  Tuesday) DAY_ZH="周二" ;;
  Wednesday) DAY_ZH="周三" ;;
  Thursday) DAY_ZH="周四" ;;
  Friday) DAY_ZH="周五" ;;
  Saturday) exit 0 ;; # 周六不进行打卡
esac

export TARGET_HEADER="## 📅 $DAY_NAME ($DAY_ZH)"
export MD_FILE_PATH="$MD_FILE"

cd "$REPO_DIR" || exit

# 1. 提取昨天 1:00 AM 到今天 1:00 AM 的代码变动 (Patch/Diff)
DIFFS=$(git log --since="$START_TIME" --until="$END_TIME" --patch --pretty=format:"Commit: %h | %s" --no-merges)

# 2. 提取修改过的文件作为文档链接归档
FILES=$(git log --since="$START_TIME" --until="$END_TIME" --name-only --pretty=format:"" | sort | uniq | grep -v '^$')

if [ -z "$DIFFS" ]; then
    export AI_SUMMARY="- [自动打卡] 今日无代码本地提交更新记录"
else
    export AI_SUMMARY="PENDING"
fi

export DIFFS_CONTENT="$DIFFS"
export FILES_CONTENT="$FILES"

# 3. 使用 Python 调用 AI 接口并安全插入文本到 Markdown
python3 - << 'EOF'
import os
import sys
import json
import urllib.request
import urllib.error

diffs = os.environ.get("DIFFS_CONTENT", "")
files = os.environ.get("FILES_CONTENT", "")
api_key = os.environ.get("API_KEY", "")
model_name = os.environ.get("MODEL_NAME", "gemini-2.5-flash")
md_file = os.environ.get("MD_FILE_PATH", "")
target_header = os.environ.get("TARGET_HEADER", "")
ai_summary = os.environ.get("AI_SUMMARY", "PENDING")

# 如果存在更新，调用 API
if ai_summary == "PENDING" and api_key and api_key != "YOUR_API_KEY_HERE":
    # 截断 diff 防止过长超过 token 限制
    truncated_diff = diffs[:20000] # Gemini token 上限很高，截取多一点没关系
    
    prompt = f"""
请根据以下 Git 提交记录和代码差异 (Diff)，写一段简明扼要的每日工作总结。
要求：
1. 语言简明清晰，用列表 (bullet points) 的形式呈现，不要寒暄。
2. 以功能维度总结，重点突出“实现了什么核心逻辑”、“修复了什么实质问题”。
3. 忽略无关紧要的格式问题、锁定文件更改或自动生成的内容。

代码差异信息如下：
{truncated_diff}
"""
    # Gemini API 格式拼装
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    data = {
        "systemInstruction": {
            "parts": [{"text": "你是一位资深的研发工程师，擅长通过代码 diff 总结工作进度报表。用中文输出。"}]
        },
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3
        }
    }
    
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req, data=json.dumps(data).encode('utf-8'), timeout=60)
        res_body = response.read()
        res_json = json.loads(res_body)
        
        # 提取 Gemini 返回的内容
        try:
            ai_summary = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        except (KeyError, IndexError) as e:
            ai_summary = f"- [自动打卡] AI 总结解析失败，原始返回：{json.dumps(res_json)[:200]}"
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        ai_summary = f"- [自动打卡] Gemini API 请求失败: HTTP {e.code}\n错误详情：{error_msg}"
    except Exception as e:
        ai_summary = f"- [自动打卡] AI 总结生成失败，报错信息：{e}"
elif ai_summary == "PENDING":
    ai_summary = "- [自动打卡] 检测到代码更新，但尚未配置有效的 API_KEY，请在脚本中填写 API 信息。"

file_links = ""
if files.strip():
    for f in files.strip().split('\n'):
        if f.strip():
            file_links += f"- `{f.strip()}`\n"
else:
    file_links = "- 无相关文档更新\n"

try:
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"File not found: {md_file}")
    sys.exit(0)

new_lines = []
in_target_day = False
target_section = None
summary_inserted = False
docs_inserted = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # 找到目标日期
    if line.strip() == target_header:
        in_target_day = True
        summary_inserted = False
        docs_inserted = False
        continue
        
    # 如果到了下一天，停止处理
    if in_target_day and line.startswith("## 📅 ") and line.strip() != target_header:
        in_target_day = False
        
    if in_target_day:
        if line.strip() == "### 📝 更新总结":
            target_section = "summary"
            continue
        elif line.strip() == "### 🔗 引用文档链接":
            target_section = "docs"
            continue
            
        if target_section == "summary" and not summary_inserted:
            if line.strip() == "-" or line.strip() == "":
                new_lines.pop() # 移除原来占位的空 '-'
            new_lines.append(ai_summary + "\n")
            target_section = None
            summary_inserted = True
            
        elif target_section == "docs" and not docs_inserted:
            if line.strip() == "-" or line.strip() == "":
                new_lines.pop() # 移除原来占位的空 '-'
            if file_links:
                new_lines.append(file_links)
            target_section = None
            docs_inserted = True

with open(md_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
EOF
