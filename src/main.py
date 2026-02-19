#!/usr/bin/env python3
#!/usr/bin/env python3
import click
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict
import random

DB_FILE = "b2b_niche_finder.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS businesses
                 (id INTEGER PRIMARY KEY, name TEXT, industry TEXT, 
                  address TEXT, phone TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pain_points
                 (id INTEGER PRIMARY KEY, industry TEXT, question TEXT, 
                  excel_pattern TEXT, saas_solution TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                 (id INTEGER PRIMARY KEY, business_id INTEGER, 
                  email_script TEXT, phone_script TEXT, roi_estimate REAL,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

@click.group()
def cli():
    """B2B Niche Finder - 发现传统行业SaaS机会"""
    init_db()

@cli.command()
@click.option('--industry', required=True, help='目标行业（如：制造业、物流、餐饮）')
@click.option('--location', required=True, help='地区（如：北京、上海）')
@click.option('--limit', default=10, help='抓取数量')
def scrape(industry, location, limit):
    """抓取本地企业信息（模拟Google Maps数据）"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 模拟企业数据（实际应调用Google Maps API）
    business_templates = [
        {"name": f"{location}{industry}有限公司{i}", "phone": f"138{random.randint(10000000, 99999999)}"}
        for i in range(1, limit + 1)
    ]
    
    for biz in business_templates:
        address = f"{location}市{random.choice(['朝阳区', '海淀区', '浦东新区', '天河区'])}XX路{random.randint(1, 999)}号"
        c.execute('''INSERT INTO businesses (name, industry, address, phone, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (biz['name'], industry, address, biz['phone'], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    click.echo(f"✓ 已抓取 {limit} 家 {industry} 企业信息")

@cli.command()
@click.option('--industry', required=True, help='目标行业')
def generate_questionnaire(industry):
    """生成行业痛点问卷模板"""
    pain_points = {
        "制造业": [
            {"q": "您目前使用Excel管理生产排程吗？", "pattern": "多sheet交叉引用、手动更新库存", 
             "solution": "生产管理SaaS：实时排程+库存预警"},
            {"q": "质检数据如何记录和追溯？", "pattern": "纸质表格扫描存档", 
             "solution": "质量追溯系统：移动端录入+自动报表"},
            {"q": "设备维护计划怎么安排？", "pattern": "Excel日历+人工提醒", 
             "solution": "设备管理系统：预防性维护+故障预测"}
        ],
        "物流": [
            {"q": "运单跟踪用什么工具？", "pattern": "Excel表格+电话确认", 
             "solution": "TMS系统：GPS实时追踪+自动通知"},
            {"q": "司机结算怎么计算？", "pattern": "Excel公式+手动核对", 
             "solution": "运费结算系统：自动计费+电子对账"}
        ],
        "餐饮": [
            {"q": "食材采购如何管理？", "pattern": "Excel采购单+微信沟通", 
             "solution": "供应链SaaS：智能补货+供应商协同"},
            {"q": "员工排班怎么做？", "pattern": "Excel班次表+群通知", 
             "solution": "排班系统：AI优化+移动打卡"}
        ]
    }
    
    questions = pain_points.get(industry, pain_points["制造业"])
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for item in questions:
        c.execute('''INSERT INTO pain_points (industry, question, excel_pattern, saas_solution)
                     VALUES (?, ?, ?, ?)''',
                  (industry, item['q'], item['pattern'], item['solution']))
    conn.commit()
    conn.close()
    
    click.echo(f"\n=== {industry} 痛点问卷 ===")
    for i, item in enumerate(questions, 1):
        click.echo(f"\n{i}. {item['q']}")
        click.echo(f"   常见Excel模式: {item['pattern']}")
        click.echo(f"   → SaaS方案: {item['solution']}")

@cli.command()
@click.option('--business-id', required=True, type=int, help='企业ID')
@click.option('--monthly-cost', default=5000, help='客户当前月成本（人民币）')
def calculate_roi(business_id, monthly_cost):
    """计算ROI和定价建议"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT name, industry FROM businesses WHERE id = ?', (business_id,))
    result = c.fetchone()
    if not result:
        click.echo("❌ 企业不存在")
        return
    
    name, industry = result
    
    # ROI计算逻辑
    efficiency_gain = 0.3  # 假设提升30%效率
    time_saved_hours = monthly_cost / 50 * efficiency_gain  # 按50元/小时计算
    annual_savings = time_saved_hours * 50 * 12
    
    # 定价策略：年节省成本的15-25%
    min_price = annual_savings * 0.15 / 12
    max_price = annual_savings * 0.25 / 12
    
    click.echo(f"\n=== {name} ROI分析 ===")
    click.echo(f"行业: {industry}")
    click.echo(f"当前月成本: ¥{monthly_cost:,.0f}")
    click.echo(f"预计效率提升: {efficiency_gain*100}%")
    click.echo(f"年节省成本: ¥{annual_savings:,.0f}")
    click.echo(f"\n💰 建议月订阅价格: ¥{min_price:,.0f} - ¥{max_price:,.0f}")
    click.echo(f"投资回收期: {(min_price*12/annual_savings)*12:.1f} 个月")
    
    conn.close()

@cli.command()
@click.option('--business-id', required=True, type=int, help='企业ID')
def generate_outreach(business_id):
    """生成冷邮件和电话脚本"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT name, industry, phone FROM businesses WHERE id = ?', (business_id,))
    result = c.fetchone()
    if not result:
        click.echo("❌ 企业不存在")
        return
    
    name, industry, phone = result
    
    c.execute('SELECT question, saas_solution FROM pain_points WHERE industry = ? LIMIT 1', (industry,))
    pain = c.fetchone()
    pain_question = pain[0] if pain else "业务流程管理"
    solution = pain[1] if pain else "数字化管理系统"
    
    email_script = f"""主题: 帮助{name}提升{industry}运营效率30%

{name}负责人您好，

我注意到贵司在{industry}领域的业务，想请教一个问题：

{pain_question}

我们服务过类似企业，通过{solution}，平均帮客户：
• 减少50%的数据录入时间
• 降低30%的人为错误
• 提升团队协作效率

方便约15分钟电话聊聊吗？我可以分享一些行业案例。

[您的姓名]
[联系方式]"""

    phone_script = f"""=== 电话脚本 ===

开场（15秒）:
"您好，请问是{name}的[决策人职位]吗？我是[公司名]的[您的名字]，专注帮助{industry}企业优化管理流程。"

痛点探测（30秒）:
"{pain_question}
我们发现很多{industry}企业在这块花费大量人力，想了解下贵司的情况。"

价值主张（30秒）:
"我们的{solution}已帮助[竞品客户]减少30%运营成本，
比如[具体案例]，投资回收期通常在6个月内。"

行动召唤:
"方便下周约个时间，我给您演示15分钟吗？或者先发份资料您看看？"

异议处理:
- "现在用Excel挺好" → "理解，很多客户最初也这么想。但当业务量增长到X时，Excel的局限就会显现..."
- "太贵了" → "我们按效果付费，如果6个月内没节省成本，全额退款。"
- "再考虑考虑" → "没问题，我发份案例给您。顺便问下，您主要顾虑是？"
"""

    c.execute('''INSERT INTO campaigns (business_id, email_script, phone_script, roi_estimate, created_at)
                 VALUES (?, ?, ?, ?, ?)''',
              (business_id, email_script, phone_script, 0.3, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    click.echo(f"\n{'='*60}")
    click.echo(email_script)
    click.echo(f"\n{'='*60}")
    click.echo(phone_script)

@cli.command()
def list_businesses():
    """列出所有企业"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, name, industry, phone FROM businesses')
    businesses = c.fetchall()
    conn.close()
    
    if not businesses:
        click.echo("暂无企业数据，请先运行 scrape 命令")
        return
    
    click.echo("\n=== 企业列表 ===")
    for biz in businesses:
        click.echo(f"ID: {biz[0]} | {biz[1]} | {biz[2]} | {biz[3]}")

@cli.command()
@click.option('--industry', required=True, help='行业名称')
def analyze_excel_patterns(industry):
    """分析Excel使用模式并给出SaaS化建议"""
    patterns = {
        "制造业": {
            "常见Excel文件": ["生产计划.xlsx", "库存台账.xlsx", "设备维护记录.xlsx"],
            "典型问题": [
                "多人同时编辑导致版本混乱",
                "公式错误导致数据不准确",
                "无法实时查看生产进度",
                "历史数据查询困难"
            ],
            "SaaS模块建议": [
                "生产排程模块：甘特图可视化+自动冲突检测",
                "库存管理模块：实时库存+安全库存预警",
                "设备管理模块：维护日历+故障工单系统",
                "数据分析模块：生产效率看板+趋势预测"
            ],
            "技术栈": "前端: React + Ant Design | 后端: Django + PostgreSQL | 部署: AWS/阿里云"
        },
        "物流": {
            "常见Excel文件": ["运单跟踪.xlsx", "司机结算.xlsx", "车辆管理.xlsx"],
            "典型问题": [
                "运单状态更新不及时",
                "结算公式复杂易出错",
                "无法实时定位车辆",
                "客户频繁电话询问进度"
            ],
            "SaaS模块建议": [
                "运单管理：状态流转+自动通知客户",
                "GPS追踪：实时地图+轨迹回放",
                "结算系统：自动计费+电子对账单",
                "客户门户：自助查询+电子签收"
            ],
            "技术栈": "前端: Vue.js + Element UI | 后端: Spring Boot + MySQL | 地图: 高德API"
        }
    }
    
    data = patterns.get(industry, patterns["制造业"])
    
    click.echo(f"\n=== {industry} Excel使用模式分析 ===\n")
    click.echo("📊 常见Excel文件:")
    for f in data["常见Excel文件"]:
        click.echo(f"  • {f}")
    
    click.echo("\n⚠️  典型痛点:")
    for p in data["典型问题"]:
        click.echo(f"  • {p}")
    
    click.echo("\n💡 SaaS化建议:")
    for s in data["SaaS模块建议"]:
        click.echo(f"  • {s}")
    
    click.echo(f"\n🛠️  推荐技术栈:\n  {data['技术栈']}")
    
    click.echo(f"\n💰 定价建议:")
    click.echo(f"  基础版: ¥999/月 (5用户)")
    click.echo(f"  专业版: ¥2999/月 (20用户 + API)")
    click.echo(f"  企业版: ¥9999/月 (无限用户 + 定制)")

if __name__ == '__main__':
    cli()