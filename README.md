智能 OCR 文字識別工具，支援繁體中文、簡體中文、英文。

## 🚀 快速開始

# 1. 安裝依賴
pip install paddlepaddle paddleocr opencv-python pillow python-docx reportlab numpy

# 2. 下載代碼
# 將 paddleocr_fixed.py 和 paddleocr_config.ini 放在同一資料夾

# 3. 測試運行
python paddleocr_fixed.py --test

# 4. 處理圖片
python paddleocr_fixed.py --file "your_image.jpg"
⚙️ 配置檔案 (paddleocr_config.ini)

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
🎯 主要功能
✅ 繁體/簡體中文 + 英文識別
✅ 批量處理：--folder "./images"
✅ 多格式輸出：TXT、DOCX、PDF
✅ AI 測試模式：--test
✅ 簡單/詳細模式切換
📝 使用範例

# 處理單檔
python paddleocr_fixed.py --file "invoice.jpg" --format pdf

# 批量處理
python paddleocr_fixed.py --folder "./documents" --lang chinese_cht

# 測試功能
python paddleocr_fixed.py --test --simple

# 查看配置
python paddleocr_fixed.py --show-config
🔧 常見問題
安裝失敗？
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple paddleocr
繁體字變簡體？

這是 PaddleOCR 模型特性，屬正常現象
找不到字體？

Windows：會自動使用微軟正黑體
其他系統：程序會使用預設字體
📦 項目檔案
paddleocr_fixed.py - 主程式
paddleocr_config.ini - 配置檔案
output/ - 輸出資料夾（自動建立）
📄 授權
MIT License - 免費使用
