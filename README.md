# Shaking Image to Generate Event Stream Pipeline

流程两步串联：
1. 对参考图像做位移抖动
2. 基于原图 + 抖动图生成event

## 参考图像放置位置

请把参考图像放在 `imgs/` 目录下，例如：

- `imgs/example.png`
- `imgs/111.png`

支持的后缀：`.png`、`.jpg`、`.jpeg`、`.bmp`

## 移动（Shake）超参数

位移相关参数在 `shaking-dynamic.py` 中：

- `shift = 5`
  - 含义：每次抖动的像素位移大小。
  - 当前会生成两种方向的位移图（上下/左右逻辑见代码）。

改抖动强度直接修改shift即可。

## 输出位置

- 抖动图输出到：`shaked_imgs/<样本名>/`
  - 例如：`shaked_imgs/example/0.jpg`

- 事件数据输出到：`evs/`
  - `*_ev.npy`：事件流
  - `*.gif`：可视化动图

## 运行方式
直接运行主脚本：

```bash
python main.py
```

