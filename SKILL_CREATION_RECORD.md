# Iterative Paper Optimization Skill - 创建记录

## 概述

基于本项目的5轮论文优化经验，我们创建了一个可复用的Claude Code skill，用于系统化地优化学术论文。

## Skill位置

```
~/.claude/skills/
├── iterative-paper-optimization.md          # 主skill文件
├── README_iterative_paper_optimization.md   # 详细文档
└── QUICKSTART.md                            # 快速开始指南
```

## Skill功能

### 核心方法

通过3-5轮迭代优化论文：

1. **Round 1: 基础增强** - 学术严谨性、文献、方法论
2. **Round 2: 深度强化** - 统计、验证、威胁分析
3. **Round 3: 出版润色** - 写作、完整性、格式
4. **Round 4+: 专项优化** - 图表、文献、特定问题

### 关键能力

- ✅ **Codex审查**: 使用codex作为外部审稿人获取专业反馈
- ✅ **文献扩展**: 自动搜索和集成30-40篇档案引用
- ✅ **图表生成**: 识别缺失图表并生成出版质量可视化
- ✅ **方法强化**: 添加统计细节、验证、敏感性分析
- ✅ **写作改进**: 重写章节、改进流畅性、优化语气
- ✅ **版本管理**: 每轮创建新版本并记录变更
- ✅ **Git集成**: 自动提交改进

## 使用方法

### 触发条件

当用户说以下内容时，Claude Code会自动使用这个skill：

```
"优化我的论文"
"改进论文准备投稿"
"review我的paper"
"帮我准备ICSE/FSE/MSR投稿"
"迭代优化论文"
```

### 基本流程

```
用户: 优化我的论文，准备投ICSE

Claude:
1. 读取当前论文版本
2. 识别目标会议（ICSE）
3. 开始Round 1审查
4. 使用codex获取反馈
5. 系统性改进（文献、实验、图表、写作）
6. 创建paper_v2.md
7. 重复3-5轮直到投稿就绪
```

## 实际效果

### 本项目案例

**优化前**:
- 6,500词草稿
- 18篇引用
- 0个图表
- 过度声明
- 方法薄弱
- **状态**: 会被拒绝

**5轮优化后**:
- 12,000词完整论文
- 45篇档案引用
- 13个图表（8主 + 5附录）
- 探索性定位
- 方法严谨
- **状态**: 边缘到弱接受（投稿就绪）

**改进**:
- Round 1: 修复学术严谨性、扩展文献
- Round 2: 加强统计和方法论
- Round 3: 完成内容和润色
- Round 4: 集成图表、修复数据不一致
- Round 5: 最终验证和数据一致性

## Skill特点

### 1. 系统化
- 结构化的轮次流程
- 明确的审查重点
- 优先级排序（关键/主要/次要）

### 2. 自动化
- 自动识别问题
- 自动生成图表
- 自动搜索文献
- 自动版本管理

### 3. 可追溯
- 每轮保存审查反馈
- 记录所有变更
- Git提交历史
- 完整优化历史

### 4. 可复用
- 适用于任何学术论文
- 支持所有主要会议/期刊
- 可定制审查重点
- 可扩展改进动作

## 技术实现

### Codex审查协议

```python
# 结构化审查提示
prompt = f"""
You are an expert academic reviewer for {venue}.
Review {paper_file} with focus on:

1. {focus_area_1}
2. {focus_area_2}
3. {focus_area_3}

Provide structured feedback:
- Overall Assessment
- Critical Issues (Must Fix)
- Major Issues (Should Fix)
- Minor Issues (Nice to Fix)
- Strengths
- Specific Recommendations
"""

# 使用codex获取反馈
codex_review = mcp__codex__codex(prompt=prompt)
```

### 改进动作

```python
# 文献扩展
WebSearch("software reusability empirical study ICSE 2024")

# 图表生成
generate_figures_script = create_visualization_script(data)
execute_script(generate_figures_script)

# 方法强化
add_statistical_details()
add_validation_analysis()
expand_threats_to_validity()

# 写作改进
rewrite_sections(issues)
improve_flow()
optimize_tone()
```

### 版本管理

```python
# 创建新版本
create_version(f"paper_v{round_num}.md", improvements)

# 记录变更
create_changelog(f"changelog_round{round_num}.md", changes)

# Git提交
git_commit(f"Round {round_num}: {focus} - {summary}")
```

## 最佳实践

### 1. 系统化执行
- 严格遵循轮次结构
- 不跳过关键问题
- 记录所有变更

### 2. 有效使用Codex
- 提供清晰、聚焦的审查提示
- 要求结构化反馈
- 请求优先级排序

### 3. 彻底解决问题
- 完全修复关键问题
- 不只是承认 - 实际修复
- 用数据验证修复

### 4. 保持一致性
- 所有数字匹配
- 一致术语
- 标准化报告

### 5. 迭代直到就绪
- 不在3轮后停止如果问题仍存在
- 每轮显示明显改进
- 最终版本无占位符

## 成功标准

论文投稿就绪时：

✅ 无占位符或草稿注释
✅ 文献达到会议标准（30-40篇）
✅ 所有数据一致
✅ 完整附录
✅ 所有图表集成
✅ 专业、自信语气
✅ 清晰贡献定位
✅ 全面威胁有效性
✅ 完整统计报告
✅ Codex审查无关键问题

## 局限性

- 不能保证接受（取决于审稿人、会议、竞争）
- 需要良好的初始内容
- 某些改进可能需要领域专业知识
- 图表生成需要数据和可视化技能
- 文献搜索限于公开可用论文

## 未来改进

可能的增强：
- [ ] 支持多种审稿人视角（不同会议风格）
- [ ] 自动化更多图表类型生成
- [ ] 集成引用管理工具
- [ ] 支持LaTeX格式
- [ ] 添加抄袭检查
- [ ] 集成语法检查工具

## 相关文档

- **Skill文件**: `~/.claude/skills/iterative-paper-optimization.md`
- **详细文档**: `~/.claude/skills/README_iterative_paper_optimization.md`
- **快速开始**: `~/.claude/skills/QUICKSTART.md`
- **本项目案例**: `paper/complete_review_history.md`
- **中文总结**: `paper/FINAL_COMPLETE_SUMMARY_CN.md`

## 版本历史

- **v1.0** (2026-03-14): 基于成功的ICSE论文优化的初始版本
  - 5轮优化流程
  - Codex审查集成
  - 文献/图表/方法/写作改进
  - 版本管理和Git集成

## 贡献者

- 基于本项目的实际优化经验创建
- 沉淀了5轮迭代的最佳实践
- 验证了从"拒绝"到"投稿就绪"的完整流程

## 许可

MIT License - 自由使用和修改

---

**创建日期**: 2026-03-14
**基于项目**: OpenClawAnalysis/software2skill_analysis
**优化案例**: ICSE论文5轮迭代优化
