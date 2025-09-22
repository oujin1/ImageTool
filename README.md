# ImageTool

一个用于裁切图片并且支持圆角导出的命令行工具。

## 安装依赖

```bash
pip install -r requirements.txt
```

如果需要运行自动化测试，请安装开发依赖：

```bash
pip install -r requirements-dev.txt
```

## 使用说明

```bash
python -m imagetool.cli INPUT_PATH OUTPUT_PATH [选项]
```

常用选项：

- `--left` 与 `--top`：裁切区域的左上角坐标，默认为 `0`。
- `--right` 与 `--bottom`：裁切区域的右下角坐标（不包含该边界）。
- `--width` 与 `--height`：可以与 `--left`、`--top` 搭配使用，通过宽高指定裁切区域。
- `--corner-radius`：圆角半径，单位为像素，默认为 `0` 表示直角。
- `--output-format`：导出格式，可选 `png`、`jpg`、`jpeg`，不指定时会根据输出文件扩展名自动判断。
- `--background-color`：在导出 JPEG 且使用圆角时用于填充透明区域的背景色，格式为 `#RRGGBB`，默认白色。

### 示例

```bash
python -m imagetool.cli input.png output.png --left 50 --top 60 --width 400 --height 300 --corner-radius 24
```

上例会将 `input.png` 从坐标 `(50, 60)` 开始裁切出 `400x300` 的区域，并在导出 `output.png` 时应用 24 像素的圆角。

```bash
python -m imagetool.cli input.png output.jpg --left 10 --top 10 --right 300 --bottom 260 --corner-radius 16 --background-color "#F0F0F0"
```

上例会导出 JPEG 文件，并使用浅灰色填充圆角处的透明区域。

## 运行测试

```bash
pytest
```
