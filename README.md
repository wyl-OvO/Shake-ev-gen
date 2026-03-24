# Shaking Image to Generate Event Stream
将图像数据集简易生成伪事件

流程两步串联：
1. 对参考图像做位移抖动
2. 基于原图 + 抖动图生成event

## Reference image

请把参考图像放在 `imgs/` 目录下，例如：

- `imgs/example.png`
- `imgs/111.png`

支持的后缀：`.png`、`.jpg`、`.jpeg`、`.bmp`

## Super Param

位移相关参数在 `shaking-dynamic.py` 中：

- `shift = 5`
  - 含义：每次抖动的像素位移大小。
  - 当前会生成两种方向的位移图（上下/左右逻辑见代码）。

改抖动强度直接修改shift即可。

## Output

- 抖动图输出到：`shaked_imgs/<样本名>/`
  - 例如：`shaked_imgs/example/0.jpg`

- 事件数据输出到：`evs/`
  - `*_ev.npy`：事件流
  - `*.gif`：可视化动图

## Excution
直接运行主脚本：

```bash
python main.py
```

