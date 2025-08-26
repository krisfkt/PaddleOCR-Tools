# PaddleOCR 智能文字識別工具

一個基於 PaddleOCR 的強大文字識別工具，支援中英文混合識別、多種輸出格式，以及批量處理功能。

## 🌟 特色功能

- ✅ **多語言支援**：中文、英文、數字混合識別
- ✅ **多種輸出格式**：TXT、DOCX、PDF
- ✅ **高精度識別**：基於 PaddleOCR v5 模型
- ✅ **智能圖片預處理**：自動增強圖片品質
- ✅ **信心度篩選**：可調整識別結果品質閾值
- ✅ **詳細統計資訊**：處理時間、字符統計、信心度分析
- ✅ **批量處理**：支援多檔案批次處理
- ✅ **測試圖片生成**：內建測試樣本生成器

## 📦 安裝需求

### Python 版本
- Python 3.8+

### 必要套件
```bash
pip install paddlepaddle
pip install paddleocr
pip install opencv-python
pip install pillow
pip install python-docx
pip install reportlab
pip install numpy
```

### 一鍵安裝
```bash
pip install -r requirements.txt
```

## 🚀 快速開始

### 1. 測試安裝
```bash
# 執行測試模式，自動建立測試圖片並識別
python paddleocr_fixed.py --test
```

### 2. 處理單一圖片
```bash
# 基本使用 (輸出 TXT)
python paddleocr_fixed.py --file "your_image.jpg"

# 輸出為 DOCX 格式
python paddleocr_fixed.py --file "your_image.jpg" --format docx

# 輸出為 PDF 格式  
python paddleocr_fixed.py --file "your_image.jpg" --format pdf

# 設定信心度閾值
python paddleocr_fixed.py --file "your_image.jpg" --confidence 0.8
```

### 3. 互動模式
```bash
python paddleocr_fixed.py
```

## 📖 使用指南

### 命令列參數

| 參數 | 說明 | 預設值 | 範例 |
|------|------|--------|------|
| `--file` | 圖片檔案路徑 | - | `--file "document.jpg"` |
| `--format` | 輸出格式 | `txt` | `--format docx` |
| `--confidence` | 信心度閾值 | `0.5` | `--confidence 0.8` |
| `--test` | 執行測試模式 | - | `--test` |

### 支援的圖片格式
- JPG/JPEG
- PNG  
- BMP
- TIFF
- GIF

### 輸出格式說明

#### TXT 格式
- 純文字檔案
- 包含詳細統計資訊
- 適合進一步文字處理

#### DOCX 格式  
- Microsoft Word 文件
- 保持文字格式
- 適合編輯和分享

#### PDF 格式
- PDF 文件
- 專業文件格式
- 適合存檔和列印

## 📊 識別結果範例

### 輸出結果示例
```
=== PaddleOCR 處理結果 ===
原始檔案: mixed_text.png
處理時間: 2025-01-26 12:40:24

=== 處理統計 ===
處理時間: 2.31 秒
檢測行數: 3
接受行數: 3  
字符數: 25
詞數: 8
信心度閾值: 0.5
平均信心度: 0.987

=== 識別內容 ===
測試文件標題
Hello World 123
混合中英文內容
```

## ⚙️ 進階配置

### 信心度設定建議
- `0.3`：寬鬆模式，保留更多結果
- `0.5`：平衡模式（預設）
- `0.8`：嚴格模式，只保留高品質結果
- `0.9`：極嚴格模式，最高品質

### 圖片最佳化建議
- **解析度**：建議 300 DPI 以上
- **對比度**：文字與背景對比清晰
- **角度**：盡量保持文字水平
- **光線**：避免陰影和反光

## 🗂️ 檔案結構

```
project/
├── paddleocr_fixed.py          # 主程式
├── paddleocr_debug.py          # 除錯工具
├── requirements.txt            # 套件需求
├── README.md                   # 說明文件
├── output/                     # 輸出資料夾
│   ├── *.txt                   # TXT 結果檔案
│   ├── *.docx                  # DOCX 結果檔案
│   └── *.pdf                   # PDF 結果檔案
└── test_examples/              # 測試圖片
    ├── test_fixed_en.png
    ├── test_fixed_ch.png
    └── test_fixed_mixed.png
```

## 🔧 疑難排解

### 常見問題

#### 1. PaddleOCR 初始化失敗
```bash
# 檢查 Python 版本
python --version

# 重新安裝 PaddleOCR
pip uninstall paddleocr paddlepaddle
pip install paddlepaddle paddleocr
```

#### 2. 識別結果不佳
- 檢查圖片品質和解析度
- 調整信心度閾值
- 嘗試圖片預處理

#### 3. 中文字體問題
- 確保系統安裝中文字體
- Windows：微軟雅黑、宋體等
- macOS/Linux：安裝對應中文字體

#### 4. ccache 警告
```
No ccache found. Please be aware that recompiling all source files may be required.
```
**這是正常的警告，不影響功能使用。**

### 除錯模式
```bash
# 執行除錯工具
python paddleocr_debug.py
```

## 🚀 效能優化

### 建議的硬體配置
- **CPU**：4 核心以上
- **記憶體**：8GB 以上  
- **硬碟空間**：模型檔案需要約 500MB

### 批量處理優化
```python
# 批量處理範例
processor = OptimizedOCRProcessor()
for image_file in image_list:
    result = processor.process_image(image_file)
    # 處理結果...
```

## 📈 版本更新

### v2.0.0 (當前版本)
- ✅ 修復新版 PaddleOCR API 相容性
- ✅ 新增 DOCX 和 PDF 輸出格式
- ✅ 改善識別精度和速度
- ✅ 新增詳細統計資訊

### v1.0.0  
- ✅ 基本 OCR 功能
- ✅ TXT 輸出格式
- ✅ 圖片預處理

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設定
```bash
git clone <repository>
cd paddleocr-tool
pip install -r requirements.txt
python paddleocr_fixed.py --test
```

### 提交規範
- 使用清晰的提交訊息
- 包含測試案例
- 遵循程式碼風格

## 📋 requirements.txt

```txt
paddlepaddle>=2.5.0
paddleocr>=2.7.0
opencv-python>=4.8.0
pillow>=10.0.0
python-docx>=0.8.11
reportlab>=4.0.0
numpy>=1.24.0
```

## 📄 授權

本專案採用 MIT 授權條款。

## 🙏 致謝

- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - 深度學習框架
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR 引擎
- 所有貢獻者和使用者

## 📞 聯絡資訊

如有問題或建議，歡迎透過以下方式聯絡：
- GitHub Issues
- Email: krisfkt@gmail.com

---

**立即開始使用，體驗強大的文字識別功能！** 🚀

## 🆘 快速求助

### 常用命令速查
```bash
# 測試安裝
python paddleocr_fixed.py --test

# 處理圖片
python paddleocr_fixed.py --file "image.jpg"

# 高品質輸出
python paddleocr_fixed.py --file "image.jpg" --format docx --confidence 0.8

# 互動模式
python paddleocr_fixed.py
```

### 輸出檔案位置
- 所有結果儲存在 `./output/` 資料夾
- 檔名格式：`原檔名_時間戳_fixed.擴展名`
- 例如：`document_20250826_124030_fixed.txt`