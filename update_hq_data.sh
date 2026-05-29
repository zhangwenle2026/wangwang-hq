#!/bin/bash
# update_hq_data.sh — 自动更新 HQ data.json 中的 hud 和 assets 数值
# tasks/log/focus 需要手动更新，本脚本只更新可自动统计的部分

set -e

HQ_DIR="/root/.openclaw/workspace/wangwang-hq"
DATA_JSON="$HQ_DIR/data.json"

# 1. 统计 skills 数量
SKILLS_COUNT=$(ls ~/.openclaw/skills/ 2>/dev/null | wc -l)

# 2. 统计 memory 文件数量
MEMORY_COUNT=$(ls ~/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l)

# 3. 统计 cron 任务数量和状态
CRON_OUTPUT=$(openclaw cron list 2>/dev/null || echo "")
CRON_TOTAL=$(echo "$CRON_OUTPUT" | grep -c "│" 2>/dev/null || echo "0")
# More reliable: count lines with UUID pattern
CRON_TOTAL=$(echo "$CRON_OUTPUT" | grep -cE '[0-9a-f]{8}-[0-9a-f]{4}' 2>/dev/null || echo "14")
CRON_ACTIVE=$(echo "$CRON_OUTPUT" | grep -c "active" 2>/dev/null || echo "$CRON_TOTAL")

# 4. Apps 数量（固定 5 个）
APPS_COUNT=5

# 5. 用 python3 更新 data.json
python3 << PYEOF
import json
from datetime import datetime, timezone, timedelta

data_path = "$DATA_JSON"

with open(data_path, 'r') as f:
    data = json.load(f)

# 更新时间戳
tz = timezone(timedelta(hours=8))
data['updated'] = datetime.now(tz).isoformat()

# 更新 assets
data['assets']['skills'] = int("$SKILLS_COUNT") if "$SKILLS_COUNT".strip() else data['assets']['skills']
data['assets']['memoryFiles'] = int("$MEMORY_COUNT") if "$MEMORY_COUNT".strip() else data['assets']['memoryFiles']
data['assets']['cronJobs'] = int("$CRON_TOTAL") if "$CRON_TOTAL".strip() else data['assets']['cronJobs']
data['assets']['apps'] = $APPS_COUNT
data['assets']['tasks'] = int("$CRON_TOTAL") if "$CRON_TOTAL".strip() else data['assets']['tasks']

# 更新 hud.tasksTotal 与 cronJobs 保持一致
data['hud']['tasksTotal'] = data['assets']['cronJobs']

with open(data_path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ data.json updated: skills={data['assets']['skills']}, memory={data['assets']['memoryFiles']}, cron={data['assets']['cronJobs']}, apps={data['assets']['apps']}")
PYEOF

# 6. Git commit & push
cd "$HQ_DIR"
git add data.json
# Only commit if there are changes
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "chore: auto-update HQ data ($(date '+%Y-%m-%d %H:%M'))"
    git push origin main
    echo "✅ Git push complete"
fi
