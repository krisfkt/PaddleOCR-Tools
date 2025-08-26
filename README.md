# 🤖 AI-Generated PaddleOCR Testing Demo Tools

智能 OCR 文字識別工具，支援繁體中文、簡體中文、英文。

## 🚀 快速開始

```bash
# 安裝依賴
pip install paddlepaddle paddleocr opencv-python pillow python-docx reportlab numpy

# 測試運行
python paddleocr_fixed.py --test

# 處理圖片
python paddleocr_fixed.py --file "your_image.jpg"
```

## ⚙️ 配置檔案 (paddleocr_config.ini)

```ini
[OCR]
lang = chinese_cht
use_angle_cls = True
use_gpu = False

[PROCESSING]
confidence_threshold = 0.9
default_output_format = pdf

[OUTPUT]
output_folder = ./output
simple_output = True
```

## 🎯 主要功能

- ✅ 繁體/簡體中文 + 英文識別
- ✅ 批量處理：`--folder "./images"`
- ✅ 多格式輸出：TXT、DOCX、PDF
- ✅ AI 測試模式：`--test`

## 📝 使用範例

```bash
# 處理單檔
python paddleocr_fixed.py --file "invoice.jpg" --format pdf

# 批量處理
python paddleocr_fixed.py --folder "./documents"

# 測試功能
python paddleocr_fixed.py --test --simple
```

## 🔧 常見問題

**安裝失敗？**

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple paddleocr
```

**繁體字變簡體？**

- 這是 PaddleOCR 模型特性，屬正常現象

## 📦 項目檔案

- `paddleocr_fixed.py` - 主程式
- `paddleocr_config.ini` - 配置檔案
- `output/` - 輸出資料夾（自動建立）

## 📄 授權

MIT License

---

🤖 AI-Generated PaddleOCR Testing Demo Tools
