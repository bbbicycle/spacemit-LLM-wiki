sidebar_position: 3

# ONNXRuntime EP FAQ

## Performance Issues

**Q: How can multiple models share and reuse compute resources?**  
**A:** If you confirm that multiple models are executed sequentially and do not interfere with each other, you can enable `SPACEMIT_EP_USE_GLOBAL_INTRA_THREAD`. This allows all models to share the same compute resources, improving overall performance through resource reuse.

**Q: What should I do if too many compute threads are launched and performance degrades?**  
**A:** If most operators in your model can be executed by the Execution Provider (EP), you can set the ONNX Runtime (ORT) thread count to `1` and use `SPACEMIT_EP_INTRA_THREAD_NUM` to control the number of threads. This helps avoid thread oversubscription and improves performance.

## Accuracy Issues

> TBD
