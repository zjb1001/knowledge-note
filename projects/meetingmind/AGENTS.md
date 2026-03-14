# GStack 配置文件 - MeetingMind

## 项目信息
- **名称**: MeetingMind
- **类型**: AI会议纪要系统
- **技术栈**: Python, 智谱GLM, PyAudio

## 团队成员

### /plan - CEO产品规划
已完成需求分析和产品方案设计

### /review - 工程经理
审查技术架构和代码质量

### /qa - QA工程师
测试功能完整性和稳定性

### /ship - 发布经理
部署和发布管理

## 关键决策
1. MVP使用智谱API，长期使用Whisper.cpp本地部署
2. 音频捕获优先支持虚拟音频设备方案
3. 纪要格式采用Markdown，便于后续处理

## 技术债务
- [ ] ASR目前使用模拟文本，需接入真实API
- [ ] 需要添加说话人分离功能
- [ ] 需要添加Teams Bot集成
