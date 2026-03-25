# 嵌入式大杂烩 - nanopb协议使用指南

## 基本信息
- **来源公众号**: 嵌入式大杂烩
- **原文链接**: https://blog.51cto.com/u_15244533/5194427
- **发布时间**: 2022-04-11

## 文章摘要
本公众号专注于嵌入式技术，包括但不限于C/C++、嵌入式、物联网、Linux等编程学习笔记，同时包含大量的学习资源。

nanopb是Protocol Buffers的纯C语言实现，适用于资源受限的嵌入式系统。本文介绍如何在嵌入式项目中使用nanopb进行数据序列化和反序列化。

## 关键要点
1. **nanopb简介**:
   - Protocol Buffers的纯C语言实现
   - 适用于资源受限的嵌入式系统
   - 代码量小，内存占用低

2. **使用流程**:
   - 编写.proto文件定义数据结构
   - 使用protoc生成C代码：`protoc --nanopb_out=. student.proto`
   - 生成student.pb.c与student.pb.h文件
   - 将Protobuf文件夹文件添加到工程并增加头文件搜索路径

3. **编码示例**:
   ```c
   uint8_t buffer[64] = {0};
   Student pack_stu = {0};
   pb_ostream_t o_stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
   pb_encode(&o_stream, Student_fields, &pack_stu);
   ```

4. **解码示例**:
   ```c
   Student unpack_stu = {0};
   pb_istream_t i_stream = pb_istream_from_buffer(buffer, sizeof(buffer));
   pb_decode(&i_stream, Student_fields, &unpack_stu);
   ```

5. **资源获取**: 公众号后台回复关键字"nanopb"获取demo代码

---
*抓取时间: 2026-03-12*
