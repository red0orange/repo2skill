# Software2Skill Analysis - 论文开发文档

## 项目概况

本项目分析了 **29,896** 个软件项目(2,200个Clawhub技能 + 27,696个GitHub仓库),研究软件的"可技能化"(skillability)特征。

## 当前文件说明

### 论文版本

1. **paper_v1.md** (完整版)
   - 状态: 已完成初稿,数据已填充
   - 字数: ~6,500词
   - 特点: 结论明确,数据完整
   - 适用: 快速投稿到arXiv或会议

2. **revised_paper_v1.md** (保守版)
   - 状态: 模板框架,包含占位符
   - 特点: 语气谨慎,强调"早期研究"
   - 适用: 需要更学术化表达的场景

3. **paper_outline_v1.md** (规划大纲)
   - 状态: 初始规划文档
   - 用途: 参考结构和投稿策略

### 数据文件

- `../output_large/paper_statistics.json` - 完整统计数据
- `../output_large/figures/` - 生成的图表
- `APPENDIX_TOP_CANDIDATES.md` - Top候选项目列表

## 核心发现

### 关键数据
- **总样本**: 29,896个项目
- **Skillability差距**: 0.86分 (Clawhub 3.75 vs GitHub 2.88)
- **高可技能化率**: 35.8% (10,698个项目)
- **最强预测维度**:
  - Automation Value (r=0.850)
  - Task Clarity (r=0.805)
- **Stars与Skillability相关性**: 仅0.143 (弱相关)

### 主要结论
1. 现有技能市场存在显著偏差
2. GitHub中有大量未被发掘的高潜力项目
3. 流行度≠可技能化程度

## 下一步工作

### 选项1: 快速投稿路径 (使用 paper_v1.md)

**时间**: 2-3天

**任务清单**:
- [ ] 生成所有图表 (使用 `generate_paper_figures.py`)
- [ ] 完善参考文献 (补充30-40篇相关论文)
- [ ] 人工验证关键数据点
- [ ] 语言润色
- [ ] 提交到 arXiv

**优点**: 快速发布,占领先机
**缺点**: 可能被认为不够谨慎

### 选项2: 学术化路径 (推荐)

**时间**: 1周

**任务清单**:
- [ ] 将 paper_v1.md 的数据填入 revised_paper_v1.md 的框架
- [ ] 补充人工验证部分 (至少200个样本)
- [ ] 完善威胁效度分析
- [ ] 添加伦理考量章节
- [ ] 生成所有图表和表格
- [ ] 完善参考文献
- [ ] 提交到 arXiv + 投稿 ICSE 2027

**优点**: 更学术化,更容易被接受
**缺点**: 需要更多时间

### 选项3: 混合路径

**时间**: 4-5天

**策略**:
1. 先用 paper_v1.md 快速发布到 arXiv (占位)
2. 同时准备 revised 版本投稿会议
3. 在 arXiv 版本中明确标注 "Preliminary Version"

## 建议的文件组织

```
paper/
├── README.md                          # 本文件
├── paper_outline_v1.md                # 保留作为参考
├── paper_v1.md                        # 重命名为 paper_draft_complete.md
├── revised_paper_v1.md                # 重命名为 paper_draft_academic.md
├── APPENDIX_TOP_CANDIDATES.md         # 保留
├── figures/                           # 创建图表目录
│   ├── fig1_skillability_distribution.png
│   ├── fig2_capability_distribution.png
│   └── ...
├── tables/                            # 创建表格目录
│   ├── table1_dataset_overview.tex
│   ├── table2_dimension_statistics.tex
│   └── ...
└── references.bib                     # 创建参考文献文件
```

## 图表生成

使用现有脚本:
```bash
cd ..
python generate_paper_figures.py
```

这将生成:
- Figure 1: Skillability Score Distribution
- Figure 2: Capability Category Distribution
- Figure 3: Dimension Radar Chart
- Figure 4: Language Distribution
- Figure 5: Granularity Distribution
- Figure 6: Execution Mode Distribution
- Figure 7: Correlation Heatmap
- Figure 8: Stars vs Skillability Scatter

## 投稿目标

### 首选 (按优先级)
1. **arXiv** (立即) - 快速发布,建立优先权
2. **ICSE 2027** (截止日期: 2026年8月) - 顶级软件工程会议
3. **FSE 2027** - 备选方案
4. **MSR 2027** - Mining Software Repositories track

### 备选
- ASE 2027 (Tool Demo + Paper)
- NeurIPS 2026 Workshop (AI Agents)

## 关键卖点

1. **规模空前**: 30K样本的大规模实证研究
2. **新颖框架**: Skillability概念首次提出
3. **可操作性**: 提供Top-100候选列表
4. **时效性**: AI Agent是当前热点
5. **可复现**: 开放数据和代码

## 联系与协作

如需讨论论文方向或数据分析,请参考:
- 数据统计: `../output_large/paper_statistics.json`
- 分析代码: `../generate_paper_statistics.py`
- 可视化: `../generate_paper_figures.py`
