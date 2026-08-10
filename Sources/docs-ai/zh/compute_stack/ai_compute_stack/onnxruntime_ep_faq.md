sidebar_position: 3

# ONNXRuntime EP FAQ

[性能问题](#性能问题)
[精度问题](#精度问题)

## 性能问题

Q: 多个模型如何复用计算资源？
> 如果确认你的多个模型是互不影响的串行执行，那么可以开启SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD，使用同一份计算资源并复用，可以提升整体性能
---

Q: 启动的计算线程数太多影响性能怎么办？
> 如果确认你的模型大多数算子可以由EP进行推理，那么可以开启选择将ORT的线程数设为1，仅使用SPACEMIT_EP_INTRA_THREAD_NUM控制线程数

## 精度问题
> TBD