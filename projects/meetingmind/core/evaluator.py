#!/usr/bin/env python3
"""
MeetingMind Evaluator - 会议纪要质量评价 Agent
负责监督和评价会议纪要的质量，提供改进建议
"""
import os
import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EvaluationResult:
    """评价结果数据结构"""
    overall_score: float  # 总分 0-100
    dimensions: Dict[str, float]  # 各维度得分
    strengths: List[str]  # 优点
    weaknesses: List[str]  # 不足
    suggestions: List[str]  # 改进建议
    action_items_quality: Dict[str, any]  # 行动项质量分析
    summary: str  # 总体评价摘要


class MeetingEvaluator:
    """
    会议纪要质量评价 Agent
    
    评价维度：
    1. 完整性 (Completeness) - 是否遗漏重要信息
    2. 准确性 (Accuracy) - 信息是否准确反映会议内容
    3. 结构化 (Structure) - 格式是否规范、层次分明
    4. 行动项 (Action Items) - Who/What/When 提取质量
    5. 可读性 (Readability) - 语言是否简洁清晰
    """
    
    def __init__(self):
        self.evaluation_criteria = {
            'completeness': {
                'weight': 0.25,
                'description': '内容完整性 - 是否覆盖会议主要议题和决策'
            },
            'accuracy': {
                'weight': 0.20,
                'description': '信息准确性 - 是否正确反映会议讨论内容'
            },
            'structure': {
                'weight': 0.20,
                'description': '结构规范性 - 格式标准、层次清晰'
            },
            'action_items': {
                'weight': 0.25,
                'description': '行动项质量 - Who/What/When 提取完整度'
            },
            'readability': {
                'weight': 0.10,
                'description': '可读性 - 语言简洁、逻辑清晰'
            }
        }
    
    def evaluate(self, transcript: str, minutes: str) -> EvaluationResult:
        """
        执行全面评价
        
        Args:
            transcript: 原始会议转录文本
            minutes: 生成的会议纪要
        
        Returns:
            EvaluationResult: 评价结果
        """
        # 各维度评价
        completeness_score = self._evaluate_completeness(transcript, minutes)
        accuracy_score = self._evaluate_accuracy(transcript, minutes)
        structure_score = self._evaluate_structure(minutes)
        action_items_result = self._evaluate_action_items(transcript, minutes)
        readability_score = self._evaluate_readability(minutes)
        
        dimensions = {
            'completeness': completeness_score,
            'accuracy': accuracy_score,
            'structure': structure_score,
            'action_items': action_items_result['score'],
            'readability': readability_score
        }
        
        # 计算总分
        overall_score = sum(
            score * self.evaluation_criteria[dim]['weight']
            for dim, score in dimensions.items()
        )
        
        # 生成优缺点和改进建议
        strengths, weaknesses, suggestions = self._generate_feedback(
            dimensions, action_items_result
        )
        
        return EvaluationResult(
            overall_score=round(overall_score, 1),
            dimensions={k: round(v, 1) for k, v in dimensions.items()},
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            action_items_quality=action_items_result,
            summary=self._generate_summary(overall_score, dimensions)
        )
    
    def _evaluate_completeness(self, transcript: str, minutes: str) -> float:
        """评价内容完整性"""
        score = 100.0
        
        # 提取转录中的关键信息点
        transcript_topics = self._extract_topics(transcript)
        minutes_topics = self._extract_topics(minutes)
        
        # 检查议题覆盖度
        if transcript_topics:
            coverage = len(minutes_topics) / len(transcript_topics)
            score = min(100, coverage * 100)
        
        # 检查参会人员
        transcript_attendees = set(re.findall(r'(\w+):', transcript))
        minutes_attendees = set(re.findall(r'参会人员[：:]\s*([^\n]+)', minutes))
        
        if not minutes_attendees:
            score -= 15
        
        # 检查是否有结论/总结
        if '会议总结' not in minutes and '总结' not in minutes:
            score -= 10
        
        return max(0, score)
    
    def _evaluate_accuracy(self, transcript: str, minutes: str) -> float:
        """评价信息准确性（启发式评估）"""
        score = 100.0
        
        # 检查关键数字/百分比是否被正确提取
        transcript_numbers = set(re.findall(r'\d+%|\d+\s*%', transcript))
        minutes_numbers = set(re.findall(r'\d+%|\d+\s*%', minutes))
        
        # 检查人名一致性
        transcript_names = set(re.findall(r'(\w+):', transcript))
        minutes_names = set(re.findall(r'[负责|执行|人][:：]\s*(\w+)', minutes))
        
        # 简单的启发式：如果行动项中的名字都在转录中，加分
        if minutes_names.issubset(transcript_names):
            score = min(100, score + 5)
        else:
            score -= 10
        
        return max(0, score)
    
    def _evaluate_structure(self, minutes: str) -> float:
        """评价结构规范性"""
        score = 100.0
        
        # 检查必备章节
        required_sections = ['基本信息', '讨论议题', '行动项']
        optional_sections = ['会议总结', '风险']
        
        for section in required_sections:
            if section not in minutes:
                score -= 15
        
        # 检查 Markdown 格式
        if '|' not in minutes:  # 缺少表格
            score -= 10
        
        if '---' not in minutes:  # 缺少分隔线
            score -= 5
        
        # 检查标题层次
        h1_count = len(re.findall(r'^# ', minutes, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', minutes, re.MULTILINE))
        
        if h1_count < 1:
            score -= 10
        if h2_count < 2:
            score -= 5
        
        return max(0, score)
    
    def _evaluate_action_items(self, transcript: str, minutes: str) -> Dict:
        """评价行动项质量"""
        result = {
            'score': 100.0,
            'count': 0,
            'with_who': 0,
            'with_what': 0,
            'with_when': 0,
            'missing_fields': []
        }
        
        # 提取行动项表格
        action_items = self._extract_action_items(minutes)
        result['count'] = len(action_items)
        
        if not action_items:
            result['score'] = 0
            result['missing_fields'] = ['无行动项']
            return result
        
        for item in action_items:
            # 检查 Who
            if item.get('负责人') or item.get('who'):
                result['with_who'] += 1
            
            # 检查 What
            if item.get('任务描述') or item.get('what'):
                result['with_what'] += 1
            
            # 检查 When
            if item.get('截止时间') or item.get('when'):
                result['with_when'] += 1
        
        # 计算完整度
        total_fields = len(action_items) * 3
        filled_fields = result['with_who'] + result['with_what'] + result['with_when']
        
        if total_fields > 0:
            result['score'] = (filled_fields / total_fields) * 100
        
        # 记录缺失字段
        if result['with_who'] < len(action_items):
            result['missing_fields'].append('部分行动项缺少负责人')
        if result['with_when'] < len(action_items):
            result['missing_fields'].append('部分行动项缺少截止时间')
        
        return result
    
    def _evaluate_readability(self, minutes: str) -> float:
        """评价可读性"""
        score = 100.0
        
        # 检查段落长度
        paragraphs = minutes.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        if long_paragraphs:
            score -= len(long_paragraphs) * 5
        
        # 检查是否有列表项
        if '-' not in minutes and '•' not in minutes:
            score -= 10
        
        # 检查冗余词汇
        redundant_words = ['这个', '那个', '然后', '就是']
        for word in redundant_words:
            if word in minutes:
                score -= 2
        
        return max(0, score)
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取文本中的议题/主题"""
        # 简单的启发式：提取包含数字或关键词的行
        topics = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # 匹配 "1. xxx" 或 "### xxx" 或 "议题" 等
            if re.match(r'^(\d+[\.、]|###|##|议题|讨论)', line):
                topics.append(line)
        
        return topics
    
    def _extract_action_items(self, minutes: str) -> List[Dict]:
        """从纪要中提取行动项"""
        items = []
        
        # 匹配表格行
        table_pattern = r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|'
        matches = re.findall(table_pattern, minutes)
        
        for match in matches:
            items.append({
                'seq': match[0].strip(),
                'who': match[1].strip(),
                'what': match[2].strip(),
                'when': match[3].strip(),
                'priority': match[4].strip(),
                'status': match[5].strip()
            })
        
        return items
    
    def _generate_feedback(self, dimensions: Dict, action_items: Dict) -> Tuple[List, List, List]:
        """生成优缺点和改进建议"""
        strengths = []
        weaknesses = []
        suggestions = []
        
        # 根据各维度得分生成反馈
        if dimensions['completeness'] >= 80:
            strengths.append("内容完整，涵盖了会议的主要议题")
        else:
            weaknesses.append("内容完整性有待提高，可能遗漏了部分讨论要点")
            suggestions.append("建议增加对会议讨论细节的捕捉，特别是关键决策点")
        
        if dimensions['structure'] >= 80:
            strengths.append("结构清晰，格式规范，层次分明")
        else:
            weaknesses.append("结构规范性不足")
            suggestions.append("建议完善 Markdown 格式，增加必要的章节分隔")
        
        if dimensions['action_items'] >= 80:
            strengths.append(f"行动项提取完整，共提取 {action_items['count']} 项")
        else:
            weaknesses.append("行动项提取质量有待提升")
            if action_items['with_who'] < action_items['count']:
                suggestions.append("部分行动项缺少负责人(Who)，建议明确责任人")
            if action_items['with_when'] < action_items['count']:
                suggestions.append("部分行动项缺少截止时间(When)，建议明确DDL")
        
        if dimensions['readability'] >= 80:
            strengths.append("语言简洁，可读性强")
        else:
            suggestions.append("建议精简语言，使用更多列表和表格提升可读性")
        
        return strengths, weaknesses, suggestions
    
    def _generate_summary(self, overall_score: float, dimensions: Dict) -> str:
        """生成总体评价摘要"""
        if overall_score >= 90:
            return "优秀 - 这是一份高质量的会议纪要，内容完整、结构清晰、行动项明确"
        elif overall_score >= 80:
            return "良好 - 纪要质量较高， minor improvements suggested"
        elif overall_score >= 70:
            return "合格 - 纪要基本可用，但在内容完整性和结构方面有提升空间"
        elif overall_score >= 60:
            return "待改进 - 纪要需要补充重要信息并优化结构"
        else:
            return "不合格 - 纪要质量较低，建议重新整理"
    
    def generate_report(self, result: EvaluationResult, output_format: str = 'markdown') -> str:
        """生成评价报告"""
        if output_format == 'markdown':
            return self._generate_markdown_report(result)
        elif output_format == 'json':
            return json.dumps({
                'overall_score': result.overall_score,
                'dimensions': result.dimensions,
                'strengths': result.strengths,
                'weaknesses': result.weaknesses,
                'suggestions': result.suggestions,
                'action_items_quality': result.action_items_quality,
                'summary': result.summary
            }, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {output_format}")
    
    def _generate_markdown_report(self, result: EvaluationResult) -> str:
        """生成 Markdown 格式评价报告"""
        report = f"""# 🎯 MeetingMind 质量评价报告

## 总体评分

<div align="center">

### {result.overall_score}/100

**{result.summary}**

</div>

---

## 各维度得分

| 评价维度 | 得分 | 权重 | 加权得分 |
|---------|------|------|---------|
| 📋 内容完整性 | {result.dimensions['completeness']} | 25% | {result.dimensions['completeness'] * 0.25:.1f} |
| ✅ 信息准确性 | {result.dimensions['accuracy']} | 20% | {result.dimensions['accuracy'] * 0.20:.1f} |
| 📐 结构规范性 | {result.dimensions['structure']} | 20% | {result.dimensions['structure'] * 0.20:.1f} |
| 🎯 行动项质量 | {result.dimensions['action_items']} | 25% | {result.dimensions['action_items'] * 0.25:.1f} |
| 📖 可读性 | {result.dimensions['readability']} | 10% | {result.dimensions['readability'] * 0.10:.1f} |

---

## 行动项分析

- **行动项总数**: {result.action_items_quality['count']} 项
- **有明确负责人**: {result.action_items_quality['with_who']} 项
- **有明确任务**: {result.action_items_quality['with_what']} 项
- **有截止时间**: {result.action_items_quality['with_when']} 项

"""
        
        if result.action_items_quality['missing_fields']:
            report += "\n### ⚠️ 发现问题\n\n"
            for issue in result.action_items_quality['missing_fields']:
                report += f"- {issue}\n"
        
        report += f"""

---

## 优点 👍

"""
        for strength in result.strengths:
            report += f"- {strength}\n"
        
        report += f"""

## 不足 ⚠️

"""
        if result.weaknesses:
            for weakness in result.weaknesses:
                report += f"- {weakness}\n"
        else:
            report += "- 无明显不足\n"
        
        report += f"""

## 改进建议 💡

"""
        for suggestion in result.suggestions:
            report += f"- {suggestion}\n"
        
        report += f"""

---

*评价时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*评价工具: MeetingMind Evaluator Agent*
"""
        
        return report


# 便捷函数
def evaluate_meeting_minutes(transcript: str, minutes: str, output_file: Optional[str] = None) -> str:
    """
    便捷函数：评价会议纪要并生成报告
    
    Args:
        transcript: 原始转录文本
        minutes: 生成的会议纪要
        output_file: 报告输出文件路径（可选）
    
    Returns:
        评价报告（Markdown格式）
    """
    evaluator = MeetingEvaluator()
    result = evaluator.evaluate(transcript, minutes)
    report = evaluator.generate_report(result, 'markdown')
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 评价报告已保存: {output_file}")
    
    return report


if __name__ == '__main__':
    # 测试示例
    test_transcript = """张三: 大家好，今天我们讨论一下Q2的产品规划。
李四: 我先说一下技术进度。后端API已经开发完成80%，预计下周可以联调。
王五: 前端进度稍微滞后，目前完成了60%。
张三: 那我们来明确一下行动项。王五负责跟进设计部原型，DDL是本周五。
李四: 收到。"""
    
    test_minutes = """# Q2产品规划会议纪要

## 基本信息
- **参会人员**: 张三、李四、王五

## 讨论议题
### 1. 后端技术进度
- **进度**: 80%完成

### 2. 前端技术进度
- **进度**: 60%完成

## 行动项
| 序号 | 负责人 | 任务描述 | 截止时间 |
|:----:|:------:|----------|----------|
| 1 | 王五 | 跟进设计部原型 | 本周五 |

## 会议总结
会议讨论了技术进度，明确了下一步行动项。
"""
    
    print("🎯 MeetingMind Evaluator Agent 测试\n")
    print("=" * 60)
    
    report = evaluate_meeting_minutes(test_transcript, test_minutes)
    print(report)
