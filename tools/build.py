"""Build the Markdown roadmap repository from its editable JSON catalog."""
from pathlib import Path
from collections import Counter
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
META = json.loads((ROOT/'data/metadata.json').read_text(encoding='utf-8'))
FAMILIES = {
 '软件产品':'software', '系统与云':'systems', '数据与决策':'data',
 'AI 与机器学习':'ai', '安全与隐私':'security', '硬件与实体系统':'hardware',
 '图形与互动':'graphics', '产品设计与交付':'product', '科研与行业交叉':'research',
 '升学与职业形态':'development', '未来工作假设':'future'
}

def put(path,text):
    dest=ROOT/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(text.rstrip()+'\n',encoding='utf-8')

def source(key):
    s=META['sources'][key]
    return f"[{s['title']}]({s['url']})"

def path(t):
    return f"roadmaps/{FAMILIES[t['family']]}/{t['id']}.md"

def safe(s):
    return escape(s,quote=True).replace('\n',' ')

def phases(t):
    if t['id'] in ['architect','em','tpm']:
        return ['本科与主线起步','工作早期','独立交付后','长期职业延伸']
    if t['id'] in ['academia','theory','quantum','alignment']:
        return ['本科基础','本科探索／研究入门','研究生或持续研究','深入研究／职业衔接']
    if t['family']=='升学与职业形态':
        return ['本科起步','确定目标与条件','针对性积累','申请或实践衔接']
    if t['status']=='未来假设':
        return ['现实基础路线','工作问题试学','小规模验证','按需求决定投入']
    return ['大二上：方向起步','大二下：主线方法','大三：实践进阶','大四及后续：交付或研究']

def prereq(t):
    f=t['family']
    if f=='硬件与实体系统':return '共同基础中的编程与系统部分；另补数字电路、电子或控制课程。芯片分支还需对应微电子基础。'
    if f=='AI 与机器学习':
        if t['id'] in ['aiapp','agents','fde','context','sandbox']:return '编程、后端、网络与数据基础；先理解模型调用与能力边界。应用入口不要求先完成预训练课程；系统分支另需 OS 与安全。'
        return '线性代数、微积分、概率统计、Python、机器学习与软件工程。训练系统分支另需 C++、体系结构与并行基础。'
    if f=='系统与云':return 'C/C++ 或相关系统语言、数据结构、组成原理、OS、网络与并发；运维入口先从 Linux 和脚本起步。'
    if f=='数据与决策':return 'SQL、Python、概率统计与数据建模；研究或优化路线按主题补证明、优化和领域知识。'
    if f=='安全与隐私':return '网络、OS、编程与安全基础；研究型密码学另补代数、概率和证明；所有攻击实践限授权对象。'
    if f=='图形与互动':return '编程、线性代数与几何；渲染需图形学，仿真另需数值方法和物理。'
    if f=='产品设计与交付':return '计算机基础认知、沟通、写作、用户与业务理解；设计需作品，管理需真实交付和团队经验。'
    if f=='科研与行业交叉':return '共同基础加对应数学与领域课程；研究目标需要持续实验室训练，不能只靠工具教程。'
    if f=='升学与职业形态':return '共同基础与一项能证明的专业能力；另核对所选国家、地区、学校或机构的当年规则。'
    if f=='未来工作假设':return '先掌握本页指定的现实基础能力；这不是已经统一确立的独立岗位培养方案。'
    return '编程、数据结构、Git、调试与测试；再按路线补网络、数据库或平台基础。'

def resource_rows(t):
    result=[]
    for i,k in enumerate(t['resources']):
        kind=META['sources'][k]['kind']
        purpose='岗位存在依据' if '招聘' in kind else ('基础／起步' if i==0 else '补充／专项')
        result.append(f"| {purpose} | {source(k)} | {kind} |")
    return '\n'.join(result)

def diagram(t):
    ps=phases(t)
    lines=['```mermaid','flowchart TB','  C["大一共同基础与方向先修"]']
    for i in range(4):
        lines.append(f'  S{i}["{safe(ps[i])}"]')
        lines.append(f'  {"C" if i==0 else "S"+str(i-1)} --> S{i}')
        for j,topic in enumerate(t[f's{i+1}'].split('；')):
            lines.append(f'  S{i} --- T{i}_{j}["{safe(topic)}"]')
    endpoint='有经验后的职业延伸' if t['id'] in ['architect','em','tpm'] else ('现实入口与假设验证' if t['status']=='未来假设' else '岗位、深造或下一阶段实践')
    lines+=['  S3 --> P["代表作与能力验收"]',f'  P --> N["{endpoint}"]','  A["全程：AI 使用、验证与责任"] -.-> S1','```']
    return '\n'.join(lines)

def build_track(t):
    c=META['familyChanges'][t['family']]
    ps=phases(t)
    stages='\n'.join(f"| {ps[i]} | {t[f's{i+1}']} |" for i in range(4))
    special=''
    if t['status']=='未来假设':
        special='\n> 这是条件性工作假设。相关技术或研究可能已经存在；这里讨论的是专门分工能否扩大，不宣称岗位尚未存在或未来必然出现。\n'
    elif t['id'] in ['architect','em','tpm']:
        special='\n> 这是有实际交付经验后的发展路线。本科阶段先进入相邻初级岗位，不以毕业直接成为架构师或管理者作为默认目标。\n'
    elif '研究' in t['entry'] or '深造' in t['entry']:
        special='\n> 年级只表示本科起步窗口。研究型目标通常还需要持续实验室或研究生训练；这不是统一学历硬门槛，也不承诺四年直接达到研究科学家水平。\n'
    p=f"""# {t['title']}

[仓库总览](../../README.md) · [本类目录](../../categories/{FAMILIES[t['family']]}.md) · [共同基础](../../docs/foundation.md) · [AI 时代调整](../../docs/ai-era.md)

| 属性 | 说明 |
| --- | --- |
| 路线类型 | {t['status']} |
| 分类 | {t['family']} |
| 入口判断 | {t['entry']} |
| 观察日期 | {t['checked']} |
| 规划性质 | 课程顺序、项目与入口判断均为综合建议；不代表统一招聘要求 |
{special}
## 开始前

{prereq(t)}

先阅读[四年共同主干](../../docs/foundation.md)。已掌握的内容通过习题或项目验收，不重复完整刷课。各分支是可选择的发展方向，不是同一学生的全部必修。

## 节点路线图

实线箭头表示建议阶段顺序；同阶段连接表示知识簇，不表示每个节点都有严格先修关系。虚线表示贯穿能力。

{diagram(t)}

## 阶段学习清单

| 建议窗口 | 课程主题与实践 |
| --- | --- |
{stages}

每个阶段至少留下可检查的代码、实验、分析或设计案例。进度依据掌握程度调整；校内必修、目标院校及岗位当年条件需单独核对。

## AI 时代怎样修改这条路线

**本路线重点：** {META['overrides'].get(t['id'],c['add'])}

| 调整 | 建议 |
| --- | --- |
| 增加 | {c['add']} |
| 保留并扎实掌握 | {c['keep']} |
| 减少重复训练 | {c['reduce']} |
| 必须识别的风险 | {c['risk']} |

减少重复训练不等于跳过基础。AI 生成的结果仍需由提交者验证；具体课程与工作单位的工具规则优先。上述调整是规划建议，不能推出某个岗位将消失。相关参考：{source(c['source'])}。

## 代表作与能力验收

**项目：** {t['project']}。

**关键验收：** {t['gate']}。

- [ ] 需求、输入、输出和限制明确。
- [ ] 代码、数据或案例来源清楚，环境与步骤可复现。
- [ ] 记录个人贡献，能脱离 AI 解释关键机制并完成现场修改。
- [ ] 有针对本路线的测试、对照、用户验证或论证。
- [ ] 保留失败案例、误差或限制，而非只展示成功结果。
- [ ] 至少获得一次外部审查：实习、开源、导师、同伴或真实用户反馈。

这是一组能力证据，不是录用保证。具体简历和选拔准备见[求职、升学与作品集](../../docs/evidence-and-entry.md)。

## 后续发展与投入

可延伸到：**{t['next']}**。转向时先补目标路线的先修，不必从所有基础课重来。

{('未来假设应以实际采用、可测收益和对应招聘为验证条件。优先保留现实岗位入口；若简单方案更优，应缩小投入。' if t['status']=='未来假设' else '本科阶段以初级入口或研究训练为目标；长远职级需要真实经验。')}

硬件路线先用仿真和学校设备；AI 路线先做小规模正确性实验并设算力预算；行业与研究路线先确认数据、导师或领域资源。不要只按路线名称购买培训或设备。

## 学习资源与依据

以下是起步资源，不是该岗位完整课表。优先选一项主资源并完成练习；目录用于查找与本页主题匹配的课程。课程可访问不表示全部作业、学分或评测免费开放。

| 用途 | 资源 | 类型 |
| --- | --- | --- |
{resource_rows(t)}

岗位族、课程与未来假设采用不同证据标准，见[来源与方法](../../docs/sources.md)。本页没有采集足以推断地区需求、薪资或录取概率的样本。
"""
    put(path(t),p)

def build_categories():
    for family,slug in FAMILIES.items():
        ts=[t for t in DATA if t['family']==family]
        graph=['```mermaid','flowchart TB',f'  F["{family}"]']+[f'  F --> R{i}["{safe(t["title"])}"]' for i,t in enumerate(ts)]+['```']
        rows='\n'.join(f"| [{t['title']}](../{path(t)}) | {t['status']} | {t['entry']} |" for t in ts)
        put(f'categories/{slug}.md',f"# {family}\n\n[返回总览](../README.md) · [先看共同基础](../docs/foundation.md)\n\n本类 {len(ts)} 条路线。下面的节点是选择分支，不需要全部学习。\n\n"+'\n'.join(graph)+f"\n\n| 路线 | 类型 | 入口判断（建议） |\n| --- | --- | --- |\n{rows}\n")

def build_readme():
    table='\n'.join(f"| [{f}](categories/{slug}.md) | {sum(t['family']==f for t in DATA)} | {'、'.join(t['title'] for t in [x for x in DATA if x['family']==f][:4])}等 |" for f,slug in FAMILIES.items())
    graph=['```mermaid','flowchart TB','  A["大一：编程、数学、工具与 AI 使用"] --> B["大二：系统基础与方向试学"]','  B --> C["选择一条主线与一项相邻能力"]']+[f'  C --> F{i}["{f}"]' for i,f in enumerate(FAMILIES)]+['  C --> D["大三：代表作与外部反馈"]','  D --> E["大四：初级岗位、升学或其他实践"]','```']
    status=Counter(t['status'] for t in DATA)
    put('README.md',f"""# AI 时代计算机学生发展路线

从大一共同基础到初级岗位、研究训练及长期职业发展。以 [roadmap.sh](https://roadmap.sh/roadmaps) 的角色目录与节点形式为参考，使用 **Markdown + Mermaid**，直接在 GitHub 阅读，无需网站、前端构建或服务部署。

**观察日期：2026-11-21。默认情境：国内四年制计算机本科；学校课程、地区与选拔规则需按个人目标调整。**

## 从哪里开始

1. 阅读[四年共同主干](docs/foundation.md)，按能力而非年级机械推进。
2. 在下面的分类中选择一条主线，打开该方向的独立路线图。
3. 阅读[AI 时代新增分工与原路线修改](docs/ai-era.md)，不要只把 AI 加成一门选修课。
4. 用[作品集与入口验收](docs/evidence-and-entry.md)检查进展；用[个人计划模板](templates/personal-plan.md)落实到当前学期。

## 发展方向总图

{chr(10).join(graph)}

## 路线目录

共 **{len(DATA)} 条方向与发展路径、{len(FAMILIES)} 个分类**，另含共同基础。数量是本仓库的编排结果，不是就业市场岗位数量；相关岗位可能在公司内合并。

| 分类 | 条目 | 示例 |
| --- | ---: | --- |
{table}

也可以查看[全部路线索引](docs/all-routes.md)，或重点看[未来工作假设](docs/future.md)。

## 每条路线包含什么

- 先修知识与方向入口。
- 节点图、阶段学习主题与建议窗口。
- AI 时代建议增加、保留、减少的训练，以及风险。
- 代表项目、可检查的能力验收与后续发展。
- 起步课程或资料，以及事实、建议和预测的边界。

## 四种不同性质的条目

| 标记 | 本仓库条目数 | 含义 |
| --- | ---: | --- |
| 现有 | {status['现有']} | 已存在的岗位族或相邻工作方向；不表示所有地区都大量招聘 |
| 新兴分工 | {status['新兴分工']} | 已有工作内容或招聘实例；独立职称和组织分工未必统一 |
| 发展路径 | {status['发展路径']} | 升学、科研、公共部门、创业、自由职业等路径，不是单个岗位 |
| 未来假设 | {status['未来假设']} | 对工作分工可能扩大的有条件判断；不是确定岗位预测 |

**“当前及未来所有岗位”无法可靠穷尽。** 本仓库覆盖主要技术族、相邻职业、行业交叉和职业形态，并提供可扩展结构。它不把工具名当独立职业，不把资深职级当本科默认出口，也不承诺按表学习即可录用。

## AI 时代的核心修改

共同基础继续保留；训练重点增加任务规格、上下文、结果验证、数据来源、权限、成本与交付责任。减少的是机械重复，不是编程、数学和系统理解。AI 应用、模型研究、训练/推理系统、评测与安全采用不同路线。

roadmap.sh 当下已包含 AI 工程、推理、MLOps、AI 红队、Agent、上下文及 FDE 等相关内容，不能笼统说这些都在其覆盖之外。本仓库额外展开训练环境、执行沙箱、人类反馈数据等分工，并在每条旧路线中加入具体调整。见[逐项对照](docs/ai-era.md)。

## 资料与使用

主要依据包括 [CS2023](https://csed.acm.org/final-report/)、[CS 自学指南](https://csdiy.wiki/)、[MIT Missing Semester](https://missing.csail.mit.edu/)、[Stanford CS336](https://cs336.stanford.edu/)、[CMU Deep Learning Systems](https://dlsyscourse.org/)、[Hugging Face Learn](https://huggingface.co/learn)、[NIST NICE](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/resources/occupations-jobs-and-work) 与 [OWASP GenAI](https://genai.owasp.org/llm-top-10/)。招聘资料只作为岗位存在的实例，不能外推整个中国就业市场。[完整来源与核验范围](docs/sources.md)。

本仓库不需要 Web 部署：上传 GitHub 仓库即可阅读；GitHub 支持 Mermaid 图表。上传步骤见[GitHub 发布说明](docs/github-publishing.md)。当前交付的是可上传的项目文件，不代表已经创建远程仓库。

## 维护

`data/catalog.json` 是路线内容源；`data/metadata.json` 保存 AI 调整与资料。修改后执行：

```bash
python tools/build.py
python tools/validate.py
```

依赖：Python 3.10+，仅标准库。校验只检查数据与仓库内部一致性，不自动证明职业判断、教学有效性或外部链接永远有效。

[贡献说明](CONTRIBUTING.md) · [更新记录](CHANGELOG.md) · [MIT License](LICENSE)
""")

def build_ai():
    rows='\n'.join(f"| {f} | {c['add']} | {c['keep']} | {c['reduce']} |" for f,c in META['familyChanges'].items() if f!='未来工作假设')
    focus=['aiapp','agents','inference','mlops','aisec','fde','context','rlenv','sandbox','aidata','humanfeedback','evals','posttrain','alignment','aigovernance']
    already={'aiapp','agents','inference','mlops','aisec','fde','context'}
    comparison=[]
    for id in focus:
        t=next(x for x in DATA if x['id']==id)
        seen='已见同名或相关独立路线' if id in already else '所查目录未见同名独立项；不等于站内没有覆盖'
        comparison.append(f"| [{t['title']}](../{path(t)}) | {t['status']} | {seen} |")
    put('docs/ai-era.md',f"""# AI 时代：新增分工与原路线修改

[返回总览](../README.md) · [全部路线](all-routes.md) · [未来假设](future.md)

观察日期：2026-11-21。本文把**核对到的现有内容、已有工作分工、作者的学习建议和未来判断**分别呈现。

## 先纠正“网站之外都是新岗位”的判断

{source('reference')} 当前目录已包含 AI Engineer、Inference Engineering、MLOps、AI Red Teaming、Forward Deployed Engineer，以及 AI Agents、Prompt & Context Engineering 等角色或技能路线。它们不能全部被称为“网站尚未覆盖的未来岗位”。

技能路线、岗位职称和公司分工也不是一一对应。NIST 对 occupation、job 与 work role 的区分可帮助避免把每个工作任务都计算成一个新职业，见 {source('nice')}。

| 本仓库展开方向 | 性质 | 与所查 roadmap.sh 目录的关系 |
| --- | --- | --- |
{chr(10).join(comparison)}

目录对照不是对其全部文章、子节点和历史版本的穷尽审计。未来维护者应重新核对，不据此声称某方向“首次出现”。

## 网站目录以外，值得进一步展开的工作

- **RL 训练环境与验证器：**把可执行任务、奖励与验证、并行运行和数据回放连接起来。
- **AI 执行沙箱与工具平台：**处理不可信执行、多租户、资源限制、身份与审计。
- **上下文与记忆工程：**管理知识、检索、工具、状态和长任务信息，独立职称尚未统一。
- **人类反馈与训练数据：**规范、质检、一致性、来源、偏差与下游验证形成闭环。
- **模型行为评测与安全：**评测设计、评分校准、污染、红队和风险控制分别需要能力。

招聘实例：{source('jobs')} 的所查目录包含环境基础设施、沙箱、后训练评测、推理系统等工作；{source('seed')} 是国内高校人才招聘实例。前者偏前沿 AI 团队，后者也是特定招聘项目，二者都不能代表所有地区与企业。

课程变化实例：{source('tools')} 的 2026 教学包含 Agentic Coding；{source('context')} 展开技能、工具连接与 Agent 生命周期。它们支持学习新工作方式，不直接证明独立岗位数量或未来薪资。

## 原有路线应该怎样改

以下为作者的综合学习建议，不是对岗位消失的预测。

| 路线族 | 建议增加 | 保留并掌握 | 减少重复训练 |
| --- | --- | --- | --- |
{rows}

各独立路线还有本方向的具体调整。减少样板、死记 API 和重复界面练习，不等于无需理解语法、数据库、网络或算法；初学者仍需足够独立实现建立判断能力。

## 所有路线的共同 AI 能力

```mermaid
flowchart LR
  A["描述任务与验收"] --> B["提供适当上下文"]
  B --> C["受控生成或执行"]
  C --> D["审查、测试与来源核验"]
  D --> E["测量质量、时间与成本"]
  E --> F["交付、监控与修正"]
```

1. 说明输入、输出、限制、可接受错误与验收方法。
2. 提供必要代码、资料、版本和权限，避免无目的堆积上下文。
3. 对执行、文件、凭证、工具和外部副作用设边界。
4. 阅读改动，查原始文档，验证引用、数据与依赖。
5. 与简单方案比较，关注失败分组、维护成本和恢复。
6. 保留独立调试、解释与修改能力，遵守课程和组织规则。

## 不应推出的结论

- 有了 Agent，不代表每个任务都需要多智能体。
- API 调用、模型微调、模型研究与推理优化不是同一能力。
- 一个热门新职称不能证明稳定收入或广泛应届入口。
- 少量海外前沿团队的招聘不能直接外推国内需求。
- AI 提高某项任务速度，不代表整个岗位价值等比例减少。

安全与工作流取舍参考：{source('owasp')}、{source('agents')}。未来的独立分工采用[条件性假设](future.md)呈现。
""")

def build_sources():
    lines=[]
    for k,s in META['sources'].items():
        lines.append(f"| `{k}` | [{s['title']}]({s['url']}) | {s['kind']} | {s['checked']} |")
    put('docs/sources.md',"""# 来源、证据与方法

[返回总览](../README.md)

## 怎样理解证据

课程框架支持知识覆盖，大学课程支持先修与教学主题，官方文档支持工具学习，招聘页面支持某类工作确实存在。它们不能互相替代。阶段安排、入口建议、项目与 AI 改造是作者的综合判断，不是引用机构背书。

本项目参考结构并独立编写中文内容，未复制 roadmap.sh 的路线图或付费资料。外部课程、作业、代码和教材保留各自许可，公开学习时也应遵守课程规则。

## 核验范围与局限

- 本轮实际访问了目录、课程首页、官方资料及招聘实例；没有审阅每个课程的全部作业。
- 部分资源是索引，不能视为专用完整课表；Apple 教程页本次只返回 JavaScript 提示。
- 未采用成功率、薪资或就业数量排名；没有足够的地区招聘样本支持这些结论。
- 国外资料不能直接代表中国市场，顶尖 AI 团队也不是普通校招的代表样本。
- 当前条目数是知识组织口径，不是岗位总量。
- 未来假设的来源仅支持现实基础问题，不能证明预测必然发生。
- 外部链接会更新；`checked` 记录本轮访问日期，不表示持续监测。

## 资料目录

| 标识 | 资料 | 类型与用途 | 本轮访问日期 |
| --- | --- | --- | --- |
"""+'\n'.join(lines)+"\n\n## 更新建议\n\n每学期检查路线与目标地区招聘，重要工具版本变化时更新专项节点。若要报告需求变化，新增明确地区、时间窗、去重规则和样本来源；不要根据单个招聘页面推断市场趋势。\n")

def build_future():
    triggers={
      'agentreliability':('长流程 Agent 被持续用于真实业务，故障恢复与权限问题成为稳定工作量','固定流程更可靠或成本更低，团队无需独立专岗'),
      'aiverify':('生成修改规模上升，验证工具能找到真实缺陷并降低维护成本','验证成本高于收益，仍由原质量与开发岗位承担'),
      'memory':('长期记忆和跨系统任务被实际采用，并需纠错、授权和删除','长期记忆需求有限，现有数据或身份团队已可覆盖'),
      'multiagent':('多智能体在具体任务上稳定优于单模型与工作流，需要运行治理','协调与通信开销抵消收益；保持单体方案更合适'),
      'humanai':('组织持续改造工作流程，并能验证质量与认知负担改善','只停留在短期演示或通用咨询，不形成稳定分工'),
      'embodiedsafety':('实体机器人部署增长，场景、仿真和安全数据形成持续闭环','部署受成本和可靠性约束，仿真不能迁移到现实'),
      'provenance':('组织需要可审计来源与责任证据，技术能提供足够可靠支持','检测误判或标准不统一，独立岗位价值不足'),
      'aicompute':('模型运行规模和资源约束使专门调度具有可测收益','现有系统优化已足够；无法直接测量真实能耗')
    }
    rows=[]
    for t in DATA:
        if t['status']=='未来假设':
            a,b=triggers[t['id']]
            rows.append(f"| [{t['title']}](../{path(t)}) | {a} | {b} | {t['next']} |")
    put('docs/future.md',"""# 未来工作假设

[返回总览](../README.md) · [现有 AI 分工](ai-era.md)

这里没有列“未来必然出现的岗位”。许多相关技术与工作已经存在，假设针对的是分工是否扩大、是否形成更多独立职称。预测没有可靠的完整清单，也不提供伪精确概率。

| 假设方向 | 成立条件 | 应降低投入的信号 | 今天的基础入口 |
| --- | --- | --- | --- |
"""+'\n'.join(rows)+"\n\n先沿现实路线积累可迁移能力，再以真实任务、组织采用和招聘信号调整。不要把未来假设当成购买设备、读某个学位或付费培训的充分依据。\n")

def main():
    for t in DATA:build_track(t)
    build_categories();build_readme();build_ai();build_sources();build_future()
    rows='\n'.join(f"| {t['family']} | [{t['title']}](../{path(t)}) | {t['status']} | {t['entry']} |" for t in DATA)
    put('docs/all-routes.md',f"# 全部路线索引\n\n[返回总览](../README.md) · [共同基础](foundation.md)\n\n共 {len(DATA)} 条方向与发展路径；一人不需要全部学习。\n\n| 分类 | 路线 | 类型 | 入口建议 |\n| --- | --- | --- | --- |\n{rows}\n")
    print(f'Built {len(DATA)} roadmaps and {len(FAMILIES)} category indexes.')

if __name__=='__main__':main()
