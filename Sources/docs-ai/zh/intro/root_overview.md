<!--
 * Copyright 2022-2023 SPACEMIT. All rights reserved.
 * Use of this source code is governed by a BSD-style license
 * that can be found in the LICENSE file.
 * 
 * @Author: David(qiang.fu@spacemit.com)
 * @Date: 2026-05-13 13:48:16
 * @LastEditTime: 2026-05-13 14:43:08
 * @FilePath: \doc\docs-ai\zh\intro\root_overview.md
 * @Description: 
-->
sidebar_position: 1

# 进迭时空 RISC-V AI 计算平台

本文档介绍了进迭时空基于***RISC-V***指令集，自研的AI计算架构。以及基于此架构，构建的基础计算软件栈和应用开发工具。另外，我们还将展示公司基于这个软件平台研发的完整demo和标杆客户的行业落地方案。

---

## 文档结构

- [第一章 解决方案](../solutions/index.md)
- [第二章 应用软件栈](../application_tools/index.md)
- [第三章 计算软件栈](../compute_stack/index.md)
- [第四章 计算架构](../architecture/index.md)

---

## 第一章 解决方案

本章系统梳理了面向【AI计算机/AI机器人/智能视觉/智能语音】等关键领域的全栈式AI解决方案，旨在清晰呈现各方案的技术路径与核心优势，助力客户基于自身需求进行高效评估与精准选型，从而加速智能产品的创新与落地进程。

- [AI Robot解决方案汇总](../solutions/airobot_solution_list.md)  
    - [AI 视觉感知](../solutions/airobot_solution_list.md)  
    - [AI 语音交互](../solutions/airobot_solution_list.md)  
    - [具身智能应用](../solutions/airobot_solution_list.md)  
    - [典型机器人场景](../solutions/airobot_solution_list.md) 
- [AI Computer解决方案汇总](../solutions/aicomputer_solution/index.md) 
    - [知了（Zenow）](../solutions/aicomputer_solution/zenow.md) 
    - [与会（Yumeet）](../solutions/aicomputer_solution/yumeet.md) 
    - [见智（Seewise）](../solutions/aicomputer_solution/seewise.md) 
    - [点将（Agentforce）](../solutions/aicomputer_solution/agentforce.md) 
    - [SpacemiT AI Lab](../solutions/aicomputer_solution/ailab.md) 

## 第二章 应用软件栈

本章旨在系统介绍AI应用软件栈，通过展示其集成流程，帮助开发者快速掌握应用部署落地的完整路径，显著降低开发门槛，提升创新效率，最终赋能多样化的端侧AI应用创新。

- [SpacemiT AI SDK](../application_tools/ai-sdk.md)
- [LangChain](../application_tools/langchain.md)
- [Ollama](../application_tools/ollama.md)
- [LocalAI](../application_tools/localai.md)


## 第三章 计算软件栈

本章将介绍进迭时空在AI计算、计算机视觉、传统高性能计算领域的软件栈建设，为客户提供多层次的全栈计算优化解决方案，其中多数推理及算子库软件均同步于开源社区。

- [AI计算软件栈](../compute_stack/ai_compute_stack.md)
- [计算机视觉库](../compute_stack/cv_library.md)
- [其他数学库](../compute_stack/math_library.md)

## 第四章 计算架构

本章详细介绍了进迭时空自研AI加速器的计算架构，主要包含设计理念和相关的指令集两个模块。

- [设计理念](../architecture/concept.md)
- [AI 指令集](../architecture/instruction.md)
