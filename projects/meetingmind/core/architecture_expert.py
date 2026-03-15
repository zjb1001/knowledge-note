#!/usr/bin/env python3
"""
MeetingMind Architecture Expert - 架构专家评审 Agent
负责从技术架构角度评审会议决策的合理性，提供架构设计建议

评审维度:
1. 技术可行性 - 决策是否在技术可实现范围内
2. 架构一致性 - 是否与现有系统架构保持一致
3. 风险评估 - 识别潜在的架构风险
4. 资源匹配 - 技术方案与资源配置是否匹配
5. 演进路径 - 长期技术演进是否可持续
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArchitectureReview:
    """架构评审结果"""
    overall_assessment: str  # 总体评估: 优秀/良好/需关注/高风险
    feasibility_score: float  # 可行性 0-100
    risk_level: str  # 风险等级: 低/中/高
    findings: List[Dict]  # 发现项
    recommendations: List[str]  # 架构建议
    tech_debt_alerts: List[str]  # 技术债务预警


class ArchitectureExpert:
    """
    架构专家评审 Agent
    
    模拟资深架构师的角色，从以下角度评审会议内容:
    - 技术决策合理性
    - 架构风险识别
    - 资源与技术匹配度
    - 长期演进可行性
    """
    
    def __init__(self):
        self.review_dimensions = {
            'feasibility': '技术可行性 - 方案是否可落地',
            'consistency': '架构一致性 - 与现有系统是否兼容',
            'scalability': '扩展性 - 未来增长是否可持续',
            'risk': '风险评估 - 潜在问题和缓解措施',
            'resource_match': '资源匹配 - 人力/时间/技术栈匹配度'
        }
    
    def review_meeting_architecture(self, minutes: str) -> str:
        """
        评审会议中的架构相关决策
        
        Args:
            minutes: 会议纪要内容
            
        Returns:
            Markdown格式的架构评审报告
        """
        # 解析会议内容
        decisions = self._extract_decisions(minutes)
        action_items = self._extract_action_items(minutes)
        risks = self._extract_risks(minutes)
        
        # 执行多维度评审
        feasibility = self._assess_feasibility(decisions, action_items)
        consistency = self._assess_consistency(decisions)
        risk_assessment = self._assess_risks(risks, action_items)
        resource_match = self._assess_resource_match(action_items)
        
        # 生成评审报告
        review = ArchitectureReview(
            overall_assessment=self._calculate_overall_assessment(
                feasibility, consistency, risk_assessment
            ),
            feasibility_score=feasibility['score'],
            risk_level=risk_assessment['level'],
            findings=self._compile_findings(
                feasibility, consistency, risk_assessment, resource_match
            ),
            recommendations=self._generate_recommendations(
                decisions, action_items, risk_assessment
            ),
            tech_debt_alerts=self._identify_tech_debt(minutes, decisions)
        )
        
        return self._generate_markdown_report(review, decisions)
    
    def _extract_decisions(self, minutes: str) -> List[Dict]:
        """提取会议决策点"""
        decisions = []
        
        # 查找决策相关文本
        decision_patterns = [
            r'明确[了]*[:：]([^\n]+)',
            r'确定[:：]([^\n]+)',
            r'决定[:：]([^\n]+)',
            r'结论[:：]([^\n]+)',
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, minutes)
            for match in matches:
                decisions.append({
                    'type': 'decision',
                    'content': match.strip()
                })
        
        return decisions
    
    def _extract_action_items(self, minutes: str) -> List[Dict]:
        """提取行动项"""
        items = []
        
        # 匹配表格中的行动项
        table_pattern = r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|'
        matches = re.findall(table_pattern, minutes)
        
        for match in matches:
            items.append({
                'seq': match[0].strip(),
                'owner': match[1].strip(),
                'task': match[2].strip(),
                'deadline': match[3].strip() if len(match) > 3 else ''
            })
        
        return items
    
    def _extract_risks(self, minutes: str) -> List[Dict]:
        """提取风险项"""
        risks = []
        
        # 查找风险表格
        risk_section = re.search(
            r'## 风险与问题\s*\n\n?(.*?)(?=##|$)',
            minutes,
            re.DOTALL
        )
        
        if risk_section:
            content = risk_section.group(1)
            # 提取表格行
            rows = re.findall(r'\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', content)
            for row in rows:
                if '问题' not in row[0] and '---' not in row[0]:
                    risks.append({
                        'issue': row[0].strip(),
                        'impact': row[1].strip(),
                        'mitigation': row[2].strip()
                    })
        
        return risks
    
    def _assess_feasibility(self, decisions: List, action_items: List) -> Dict:
        """评估技术可行性"""
        score = 85.0
        concerns = []
        
        # 检查是否有明确的技术方案
        if not decisions:
            score -= 15
            concerns.append("缺乏明确的技术决策")
        
        # 检查行动项是否可执行
        for item in action_items:
            task = item.get('task', '')
            # 检查是否有模糊表述
            if any(word in task for word in ['协调', '跟进', '支持']):
                if '具体' not in task and '详细' not in task:
                    score -= 5
                    concerns.append(f"行动项'{task}'缺乏具体技术细节")
        
        # 检查时间可行性
        tight_schedule = sum(1 for item in action_items if '本周' in item.get('deadline', ''))
        if tight_schedule > 2:
            score -= 10
            concerns.append("本周任务过于集中，存在延期风险")
        
        return {
            'score': max(0, score),
            'concerns': concerns,
            'assessment': '可行' if score >= 70 else '需谨慎'
        }
    
    def _assess_consistency(self, decisions: List) -> Dict:
        """评估架构一致性"""
        # 检查决策是否与常见架构原则冲突
        issues = []
        
        for decision in decisions:
            content = decision.get('content', '')
            # 检查是否有架构反模式
            if '临时' in content and '方案' in content:
                issues.append("检测到'临时方案'，建议评估长期影响")
            
            if '绕过' in content or '跳过' in content:
                issues.append("检测到可能绕开标准流程的决策，需架构审查")
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'score': 100 - len(issues) * 15
        }
    
    def _assess_risks(self, risks: List, action_items: List) -> Dict:
        """评估风险等级"""
        risk_score = 0
        
        # 根据风险数量评估
        if not risks:
            risk_score = 30  # 未识别风险本身就是风险
        else:
            risk_score = len(risks) * 20
        
        # 检查是否有缓解措施
        unmitigated = sum(1 for r in risks if not r.get('mitigation'))
        risk_score += unmitigated * 15
        
        # 确定风险等级
        if risk_score < 30:
            level = '低'
        elif risk_score < 60:
            level = '中'
        else:
            level = '高'
        
        return {
            'level': level,
            'score': risk_score,
            'unmitigated': unmitigated,
            'recommendations': [
                "建议为高风险项制定详细缓解计划" if level == '高' else "风险可控"
            ]
        }
    
    def _assess_resource_match(self, action_items: List) -> Dict:
        """评估资源匹配度"""
        # 分析资源分配
        owner_tasks = {}
        for item in action_items:
            owner = item.get('owner', '未知')
            owner_tasks[owner] = owner_tasks.get(owner, 0) + 1
        
        imbalances = []
        avg_tasks = len(action_items) / max(len(owner_tasks), 1)
        
        for owner, count in owner_tasks.items():
            if count > avg_tasks * 1.5:
                imbalances.append(f"{owner}任务负荷过高({count}项)")
        
        return {
            'balanced': len(imbalances) == 0,
            'owner_distribution': owner_tasks,
            'imbalances': imbalances
        }
    
    def _calculate_overall_assessment(self, feasibility, consistency, risk) -> str:
        """计算总体评估等级"""
        scores = [
            feasibility['score'],
            consistency['score'],
            100 - risk['score']  # 风险分越低越好
        ]
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 85:
            return "优秀"
        elif avg_score >= 70:
            return "良好"
        elif avg_score >= 60:
            return "需关注"
        else:
            return "高风险"
    
    def _compile_findings(self, feasibility, consistency, risk, resource) -> List[Dict]:
        """编译评审发现"""
        findings = []
        
        # 可行性发现
        if feasibility['concerns']:
            findings.append({
                'category': '技术可行性',
                'severity': '中',
                'items': feasibility['concerns']
            })
        
        # 一致性发现
        if consistency['issues']:
            findings.append({
                'category': '架构一致性',
                'severity': '高',
                'items': consistency['issues']
            })
        
        # 资源匹配发现
        if resource['imbalances']:
            findings.append({
                'category': '资源分配',
                'severity': '中',
                'items': resource['imbalances']
            })
        
        return findings
    
    def _generate_recommendations(self, decisions, action_items, risk) -> List[str]:
        """生成架构建议"""
        recommendations = []
        
        # 基于决策的建议
        if len(decisions) < 2:
            recommendations.append("建议补充更详细的技术决策点，明确架构方向")
        
        # 基于行动项的建议
        if action_items:
            high_priority = sum(1 for item in action_items if '高' in item.get('task', ''))
            if high_priority > 2:
                recommendations.append("高优先级任务较多，建议进行任务排序和依赖分析")
        
        # 基于风险的建议
        if risk['level'] == '高':
            recommendations.append("当前架构风险较高，建议召开架构评审会议")
        
        recommendations.extend([
            "建议在下次会议中回顾技术债务处理进展",
            "建议建立技术方案文档，确保知识沉淀"
        ])
        
        return recommendations
    
    def _identify_tech_debt(self, minutes: str, decisions: List) -> List[str]:
        """识别技术债务信号"""
        alerts = []
        
        # 检测技术债务关键词
        debt_signals = [
            (r'临时方案|临时解决', "检测到临时方案，建议规划长期解决计划"),
            (r'绕过|规避|跳过', "检测到绕过标准流程的做法，需评估技术债务"),
            (r'后期优化|以后再|先这样', "存在推迟优化的倾向，建议记录技术债务"),
            (r'手动|人工', "检测到手动操作，建议评估自动化可行性"),
        ]
        
        for pattern, alert in debt_signals:
            if re.search(pattern, minutes):
                alerts.append(alert)
        
        return alerts
    
    def _generate_markdown_report(self, review: ArchitectureReview, decisions: List) -> str:
        """生成Markdown格式评审报告"""
        report = f"""# 🏛️ Architecture Expert 评审报告

## 总体评估

| 指标 | 结果 |
|------|------|
| **总体等级** | {review.overall_assessment} |
| **可行性评分** | {review.feasibility_score:.0f}/100 |
| **风险等级** | {review.risk_level} |

---

## 评审发现

"""
        
        if review.findings:
            for finding in review.findings:
                severity_emoji = '🔴' if finding['severity'] == '高' else '🟡'
                report += f"### {severity_emoji} {finding['category']} ({finding['severity']}风险)\n\n"
                for item in finding['items']:
                    report += f"- {item}\n"
                report += "\n"
        else:
            report += "✅ 未发现重大架构问题\n\n"
        
        # 技术债务预警
        if review.tech_debt_alerts:
            report += "## ⚠️ 技术债务预警\n\n"
            for alert in review.tech_debt_alerts:
                report += f"- {alert}\n"
            report += "\n"
        
        # 架构建议
        report += "## 💡 架构专家建议\n\n"
        for i, rec in enumerate(review.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        # 决策点评
        if decisions:
            report += """

## 📝 关键决策点评

| 决策 | 架构视角评估 |
|------|-------------|
"""
            for i, decision in enumerate(decisions[:5], 1):
                content = decision['content'][:30] + "..." if len(decision['content']) > 30 else decision['content']
                report += f"| {i}. {content} | 需进一步技术评估 |\n"
        
        report += f"""

---

*评审时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*评审工具: MeetingMind Architecture Expert*
*免责声明: 本评审基于会议纪要内容，具体实施需结合实际情况*
"""
        
        return report


# 便捷函数
def review_architecture(minutes: str) -> str:
    """便捷函数：评审会议纪要架构"""
    expert = ArchitectureExpert()
    return expert.review_meeting_architecture(minutes)


if __name__ == '__main__':
    # 测试示例
    test_minutes = """# 测试会议

## 决策
确定使用临时方案解决当前问题，后期再进行优化。

## 行动项
| 负责人 | 任务 |
|--------|------|
| 张三 | 协调资源 |
| 李四 | 临时修复 |
"""
    
    print("🏛️ Architecture Expert 测试\n")
    print(ArchitectureExpert().review_meeting_architecture(test_minutes))
