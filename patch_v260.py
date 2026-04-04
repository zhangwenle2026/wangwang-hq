#!/usr/bin/env python3
"""wangwang-hq v2.6.0 patch script"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# ============================================================
# 改项4+5: 在 </style> 前插入新 CSS
# ============================================================
archi_css = """/* === 阿奇主角效果 === */
.archi-hero-wrap{position:relative;display:flex;align-items:center;justify-content:center;width:130px;height:130px;margin-bottom:4px}
.archi-glow-ring{position:absolute;inset:0;border-radius:50%;border:2px solid rgba(138,92,246,0.4);animation:glowPulse 2s ease-in-out infinite}
.archi-glow-ring2{inset:-8px;border-color:rgba(96,165,250,0.25);animation-delay:1s}
@keyframes glowPulse{0%,100%{transform:scale(1);opacity:0.7}50%{transform:scale(1.12);opacity:1}}
.archi-av-wrap{position:relative;width:110px;height:110px;z-index:1}
.archi-av{width:110px;height:110px;border-radius:50%;object-fit:cover;animation:archiBreath 3s ease-in-out infinite;border:3px solid rgba(138,92,246,0.5);display:block}
@keyframes archiBreath{0%,100%{box-shadow:0 0 20px rgba(138,92,246,0.4)}50%{box-shadow:0 0 40px rgba(138,92,246,0.7),0 0 60px rgba(96,165,250,0.3)}}
/* XP 进度条 */
.archi-xp-bar-wrap{width:100%;margin:6px 0 2px}
.archi-xp-bar-bg{width:100%;height:6px;background:rgba(138,92,246,0.15);border-radius:10px;overflow:hidden}
.archi-xp-bar-fill{height:100%;background:linear-gradient(90deg,#818cf8,#a78bfa);border-radius:10px;animation:xpFill 1.5s ease-out forwards;transform-origin:left}
@keyframes xpFill{0%{width:0%}100%{width:72%}}
.archi-xp-label{font-size:9px;color:rgba(25,118,210,0.6);font-weight:700;text-align:right;margin-top:2px}
/* 全局留白收紧 */
.panel{padding:16px}
.panel-header{margin-bottom:14px}
.growth-grid{gap:12px}
.main{padding:16px 20px 32px;gap:16px}
.hb-ecg-wrap{padding:6px 14px;margin-bottom:12px}
.hb-ecg-svg{height:36px}
"""

content = content.replace('</style>', archi_css + '</style>', 1)
print("✅ 改项4+5: 新增CSS插入完成")

# ============================================================
# 改项1: 替换成员卡片的 onclick → onmouseenter+onmouseleave
# ============================================================
old_onclick = 'onclick="(function(el){var tip=el.querySelector(\'.mc-tooltip\');if(!tip)return;var show=tip.classList.contains(\'tip-show\');tip.classList.toggle(\'tip-show\');el.style.transform=show?\'\':\' translateY(-4px) scale(1.03)\';if(show)setTimeout(function(){el.style.transform=\'\'},200)})(this)"'

new_hover = 'onmouseenter="(function(el){var t=el.querySelector(\'.mc-tooltip\');if(t)t.classList.add(\'tip-show\')})(this)" onmouseleave="(function(el){var t=el.querySelector(\'.mc-tooltip\');if(t)t.classList.remove(\'tip-show\')})(this)"'

# The actual onclick string in the file (without escaped quotes since we read raw)
# Let's do a direct string search
old_onclick_raw = """onclick="(function(el){var tip=el.querySelector('.mc-tooltip');if(!tip)return;var show=tip.classList.contains('tip-show');tip.classList.toggle('tip-show');el.style.transform=show?'':'translateY(-4px) scale(1.03)';if(show)setTimeout(function(){el.style.transform=''},200)})(this)\""""

new_hover_raw = """onmouseenter="(function(el){var t=el.querySelector('.mc-tooltip');if(t)t.classList.add('tip-show')})(this)" onmouseleave="(function(el){var t=el.querySelector('.mc-tooltip');if(t)t.classList.remove('tip-show')})(this)\""""

count_before = content.count("onclick=\"(function(el){var tip=el.querySelector('.mc-tooltip')")
print(f"onclick mc-tooltip occurrences before: {count_before}")

content = content.replace(old_onclick_raw, new_hover_raw)

count_after = content.count("onclick=\"(function(el){var tip=el.querySelector('.mc-tooltip')")
count_hover = content.count("onmouseenter=")
print(f"onclick mc-tooltip occurrences after: {count_after}")
print(f"onmouseenter occurrences: {count_hover}")
print("✅ 改项1: onclick → hover 替换完成")

# ============================================================
# 改项2: 替换 archi-col 内部内容（保留 img 标签）
# ============================================================
lines = content.split('\n')

# Find archi-col line
archi_col_start = None
archi_col_end = None
img_line = None

for i, line in enumerate(lines):
    if '<div class="archi-col">' in line and archi_col_start is None:
        archi_col_start = i
        print(f"Found archi-col at line {i+1}: {line[:60]}")
    
    # Find the img tag within archi-col section
    if archi_col_start is not None and archi_col_end is None:
        if '<img' in line and 'data:image' in line:
            img_line = line
            print(f"Found img at line {i+1}, length: {len(line)}")
        
        # Find the closing </div> of archi-col
        # Look for the line that is just "      </div>" after we've found the content
        if i > archi_col_start + 1 and '</div>' in line and '<!--' not in line:
            # Check if this is the closing tag of archi-col by looking at context
            # The archi-col ends with a simple </div> line
            stripped = line.strip()
            if stripped == '</div>' and i > archi_col_start + 3:
                archi_col_end = i
                print(f"Found archi-col end at line {i+1}: '{line}'")
                break

print(f"archi-col range: {archi_col_start+1} to {archi_col_end+1}")

if img_line and archi_col_start is not None and archi_col_end is not None:
    # Get the indentation of archi-col
    indent = '      '
    
    # Build new inner content
    new_inner = [
        f'{indent}  <div class="archi-hero-wrap">',
        f'{indent}    <div class="archi-glow-ring"></div>',
        f'{indent}    <div class="archi-glow-ring archi-glow-ring2"></div>',
        f'{indent}    <div class="archi-av-wrap">',
        f'{indent}      {img_line.strip()}',
        f'{indent}      <div class="archi-tip">嗨！今天也要一起加油哦 🐾</div>',
        f'{indent}    </div>',
        f'{indent}  </div>',
        f'{indent}  <div class="archi-name">阿奇 · Archi</div>',
        f'{indent}  <div class="archi-level">⭐ <b>Lv.5</b> <span>成长中</span></div>',
        f'{indent}  <div class="archi-xp-bar-wrap">',
        f'{indent}    <div class="archi-xp-bar-bg">',
        f'{indent}      <div class="archi-xp-bar-fill" style="width:72%"></div>',
        f'{indent}    </div>',
        f'{indent}    <div class="archi-xp-label">XP 720 / 1000</div>',
        f'{indent}  </div>',
        f'{indent}  <div class="archi-companion" id="archi-companion">🤝 陪伴你已经 计算中...</div>',
        f'{indent}  <div class="archi-quote-box">',
        f'{indent}    <div class="archi-quote-label">💬 每日心情</div>',
        f'{indent}    <div class="archi-quote-text" id="archiDailyQuote">今天也要元气满满地工作！每一个任务都是成长的足迹。✨</div>',
        f'{indent}  </div>',
    ]
    
    # Replace lines[archi_col_start+1 : archi_col_end] with new_inner
    new_lines = lines[:archi_col_start+1] + new_inner + lines[archi_col_end:]
    content = '\n'.join(new_lines)
    print(f"✅ 改项2: archi-col 内容替换完成")
else:
    print(f"❌ 改项2: 未找到必要元素! img_line={img_line is not None}, start={archi_col_start}, end={archi_col_end}")

# ============================================================
# 改项3a: 今日日志 → 历史日志
# ============================================================
content = content.replace('<div class="sidebar-section-title">📋 今日日志</div>',
                          '<div class="sidebar-section-title">📋 历史日志</div>', 1)
print("✅ 改项3a: 今日日志 → 历史日志")

# ============================================================
# 改项3b: 给 .sb-timeline 加滚动 CSS（已在改项4+5中处理了</style>，这里追加到已有sb-timeline CSS前面)
# 实际上改项4+5已经在</style>前插入了，但滚动CSS要另外追加
# ============================================================
sb_timeline_css = """.sb-timeline{max-height:280px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,0.3) transparent}
.sb-timeline::-webkit-scrollbar{width:3px}
.sb-timeline::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.3);border-radius:3px}
"""
# Insert before </style>
content = content.replace('</style>', sb_timeline_css + '</style>', 1)
print("✅ 改项3b: .sb-timeline 滚动CSS追加完成")

# ============================================================
# 改项3c: 在 sb-timeline 结束前插入历史日志条目
# ============================================================
history_entries = """      <div class="sb-tl">
        <div class="sb-tl-dc"><div class="sb-tl-dot b"></div><div class="sb-tl-line"></div></div>
        <div class="sb-tl-content"><div class="sb-tl-time">03-24 BRT</div><div class="sb-tl-text">🐾 阿奇诞生</div><div class="sb-tl-sub">LingLing 正式上线</div></div>
      </div>
      <div class="sb-tl">
        <div class="sb-tl-dc"><div class="sb-tl-dot g"></div><div class="sb-tl-line"></div></div>
        <div class="sb-tl-content"><div class="sb-tl-time">03-25 BRT</div><div class="sb-tl-text">✅ 首次发群消息</div><div class="sb-tl-sub">AI Eric 机器人打通</div></div>
      </div>
      <div class="sb-tl">
        <div class="sb-tl-dc"><div class="sb-tl-dot b"></div><div class="sb-tl-line"></div></div>
        <div class="sb-tl-content"><div class="sb-tl-time">03-30 BRT</div><div class="sb-tl-text">📚 BEC 英语网站上线</div><div class="sb-tl-sub">CAP-004 圣托里尼风格</div></div>
      </div>
      <div class="sb-tl">
        <div class="sb-tl-dc"><div class="sb-tl-dot g"></div><div class="sb-tl-line"></div></div>
        <div class="sb-tl-content"><div class="sb-tl-time">04-02 BRT</div><div class="sb-tl-text">🔗 A2A 通信打通</div><div class="sb-tl-sub">汪汪队全员上线</div></div>
      </div>
      <div class="sb-tl">
        <div class="sb-tl-dc"><div class="sb-tl-dot b"></div><div class="sb-tl-line"></div></div>
        <div class="sb-tl-content"><div class="sb-tl-time">04-03 BRT</div><div class="sb-tl-text">🏠 HQ v1.0 上线</div><div class="sb-tl-sub">汪汪队指挥中心</div></div>
      </div>
    </div>"""

# Find the closing of sb-timeline: "    </div>" after the last sb-tl entry
# The sb-timeline div closes with "    </div>\n  </div>" pattern
# We need to find "    </div>" that closes the sb-timeline
# Looking at the structure: sb-timeline ends with </div> then </div> for sidebar-section

# Find closing of sb-timeline
old_timeline_end = """      </div>
    </div>
  </div>

  <div class="sidebar-divider"></div>"""

new_timeline_end = history_entries + """

  </div>

  <div class="sidebar-divider"></div>"""

if old_timeline_end in content:
    content = content.replace(old_timeline_end, new_timeline_end, 1)
    print("✅ 改项3c: 历史日志条目插入完成")
else:
    print("❌ 改项3c: 未找到 sb-timeline 结束标记，尝试备用方案")
    # Try alternative
    # Find the sb-timeline closing div
    idx = content.find('<div class="sb-timeline">')
    if idx >= 0:
        # Find the matching closing </div>
        # Count div depth
        search_start = idx + len('<div class="sb-timeline">')
        depth = 1
        pos = search_start
        while pos < len(content) and depth > 0:
            open_tag = content.find('<div', pos)
            close_tag = content.find('</div>', pos)
            if open_tag == -1 and close_tag == -1:
                break
            if open_tag != -1 and (close_tag == -1 or open_tag < close_tag):
                depth += 1
                pos = open_tag + 4
            else:
                depth -= 1
                if depth == 0:
                    # Insert before this closing </div>
                    content = content[:close_tag] + history_entries.rsplit('</div>', 1)[0] + '\n' + content[close_tag:]
                    print("✅ 改项3c: 历史日志条目插入完成（备用方案）")
                    break
                pos = close_tag + 6

# ============================================================
# 改项3d: 追加自动滚到底部的脚本
# ============================================================
scroll_script = """<script>
(function(){var tl=document.querySelector('.sb-timeline');if(tl)tl.scrollTop=tl.scrollHeight})();
</script>
</body>"""

content = content.replace('</body>', scroll_script, 1)
print("✅ 改项3d: 自动滚底脚本追加完成")

# ============================================================
# 版本号 2.5.0 → 2.6.0
# ============================================================
content = content.replace('2.5.0', '2.6.0')
v260_count = content.count('2.6.0')
print(f"✅ 版本号更新: 2.6.0 出现 {v260_count} 次")

# ============================================================
# 写回文件
# ============================================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 所有改项完成，文件已写回！")

# ============================================================
# 验证
# ============================================================
print("\n=== 验证结果 ===")
with open('index.html') as f:
    h = f.read()
print(f"v2.6.0: {h.count('2.6.0')}")
print(f"onmouseenter count: {h.count('onmouseenter')}")
onclick_mc_count = h.count("onclick=\"(function(el){var tip=el.querySelector('.mc-tooltip')")
print(f"onclick mc count: {onclick_mc_count}")
print(f"archi-glow-ring: {h.count('archi-glow-ring')}")
print(f"archi-xp-bar: {h.count('archi-xp-bar')}")
print(f"历史日志: {h.count('历史日志')}")
