# paddleocr_fixed.py
import os
import time
import json
import argparse
import configparser
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 核心套件
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCR

# 文件處理
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# PDF 生成
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PaddleOCRResultParser:
    """PaddleOCR 結果解析器 - 適配新版 API"""
    
    @staticmethod
    def extract_text_from_result(result) -> Tuple[str, List[Dict]]:
        """從新版 PaddleOCR 結果中提取文字"""
        text_lines = []
        detailed_results = []
        
        try:
            if isinstance(result, list) and len(result) > 0:
                # 新版返回 OCRResult 物件
                ocr_result = result[0]
                
                # 檢查是否有 rec_texts 屬性（識別的文字）
                if hasattr(ocr_result, 'rec_texts') and ocr_result.rec_texts:
                    texts = ocr_result.rec_texts
                    scores = getattr(ocr_result, 'rec_scores', [1.0] * len(texts))
                    polys = getattr(ocr_result, 'rec_polys', [None] * len(texts))
                    
                    for i, text in enumerate(texts):
                        confidence = scores[i] if i < len(scores) else 1.0
                        poly = polys[i] if i < len(polys) else None
                        
                        text_lines.append(text)
                        detailed_results.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': poly.tolist() if poly is not None else None
                        })
                
                # 如果是字典格式（向後兼容）
                elif isinstance(ocr_result, dict):
                    if 'rec_texts' in ocr_result and ocr_result['rec_texts']:
                        texts = ocr_result['rec_texts']
                        scores = ocr_result.get('rec_scores', [1.0] * len(texts))
                        polys = ocr_result.get('rec_polys', [None] * len(texts))
                        
                        for i, text in enumerate(texts):
                            confidence = scores[i] if i < len(scores) else 1.0
                            poly = polys[i] if i < len(polys) else None
                            
                            text_lines.append(text)
                            detailed_results.append({
                                'text': text,
                                'confidence': confidence,
                                'bbox': poly.tolist() if poly is not None else None
                            })
        
        except Exception as e:
            print(f"結果解析錯誤: {e}")
        
        return '\n'.join(text_lines), detailed_results


import configparser

class OptimizedOCRProcessor:
    def __init__(self, config_file: str = "paddleocr_config.ini"):
        self.config_file = config_file
        self.ocr_engine = None
        self.parser = PaddleOCRResultParser()
        self.config = self._load_config()
        self._init_ocr_engine()
    
    def _load_config(self):
        """載入配置檔案"""
        config = configparser.ConfigParser()
        
        # 預設配置
        default_config = {
            'OCR': {
                'lang': 'ch',
                'use_angle_cls': 'True',
                'use_gpu': 'False',
                'show_log': 'False'
            },
            'PROCESSING': {
                'confidence_threshold': '0.5',
                'default_output_format': 'txt'
            }
        }
        
        # 如果配置檔案存在，讀取它
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file, encoding='utf-8')
                print(f"✓ 載入配置檔案: {self.config_file}")
            except Exception as e:
                print(f"✗ 配置檔案讀取失敗: {e}")
                print("使用預設配置")
        else:
            # 創建預設配置檔案
            for section, options in default_config.items():
                config.add_section(section)
                for key, value in options.items():
                    config.set(section, key, value)
            
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                print(f"✓ 創建預設配置檔案: {self.config_file}")
            except Exception as e:
                print(f"✗ 配置檔案創建失敗: {e}")
        
        return config
    
    def _init_ocr_engine(self):
        """根據配置初始化 OCR 引擎"""
        try:
            print("正在初始化 PaddleOCR 引擎...")
            
            # 從配置檔案獲取參數
            ocr_config = {}
            if self.config.has_section('OCR'):
                ocr_config['lang'] = self.config.get('OCR', 'lang', fallback='ch')
                ocr_config['use_angle_cls'] = self.config.getboolean('OCR', 'use_angle_cls', fallback=True)
                ocr_config['use_gpu'] = self.config.getboolean('OCR', 'use_gpu', fallback=False)
                
                # show_log 在新版本可能不支援，所以先嘗試
                try:
                    show_log = self.config.getboolean('OCR', 'show_log', fallback=False)
                    ocr_config['show_log'] = show_log
                except:
                    pass
            
            # 備用配置（如果配置檔案失敗）
            configs_to_try = [
                ocr_config,
                {'lang': 'ch'},
                {'lang': 'en'},
            ]
            
            for config in configs_to_try:
                try:
                    print(f"嘗試配置: {config}")
                    self.ocr_engine = PaddleOCR(**config)
                    self.current_config = config
                    print(f"✓ 成功初始化，配置: {config}")
                    break
                except Exception as e:
                    print(f"✗ 配置失敗: {e}")
            
            if self.ocr_engine is None:
                raise Exception("所有配置都失敗")
                
        except Exception as e:
            print(f"OCR 初始化失敗: {e}")
            self.ocr_engine = None
    
    def process_image(self, image_path: str, confidence_threshold: float = 0.5) -> Dict:
        """處理圖片檔案"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"找不到圖片檔案: {image_path}")
        
        if self.ocr_engine is None:
            raise RuntimeError("PaddleOCR 引擎未初始化")
        
        print(f"開始處理圖片: {image_path}")
        start_time = time.time()
        
        try:
            # 載入圖片
            image = cv2.imread(image_path)
            if image is None:
                pil_image = Image.open(image_path)
                image = np.array(pil_image)
                if len(image.shape) == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 執行 OCR
            print("正在執行 OCR 識別...")
            
            try:
                results = self.ocr_engine.predict(image)
            except AttributeError:
                results = self.ocr_engine.ocr(image)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 解析結果
            text_content, detailed_results = self.parser.extract_text_from_result(results)
            
            # 過濾低信心度結果
            filtered_results = []
            filtered_text_lines = []
            
            for result in detailed_results:
                if result['confidence'] >= confidence_threshold:
                    filtered_results.append(result)
                    filtered_text_lines.append(result['text'])
            
            filtered_text = '\n'.join(filtered_text_lines)
            
            # 統計資訊
            stats = {
                'processing_time': f"{processing_time:.2f} 秒",
                'total_detected': len(detailed_results),
                'accepted_lines': len(filtered_results),
                'total_chars': len(filtered_text),
                'total_words': len(filtered_text.split()),
                'confidence_threshold': confidence_threshold,
                'average_confidence': sum(r['confidence'] for r in filtered_results) / len(filtered_results) if filtered_results else 0
            }
            
            print(f"✓ OCR 完成")
            print(f"  檢測到: {stats['total_detected']} 行")
            print(f"  接受: {stats['accepted_lines']} 行")
            print(f"  字符數: {stats['total_chars']}")
            print(f"  平均信心度: {stats['average_confidence']:.3f}")
            
            return {
                'text_content': filtered_text,
                'all_text': text_content,  # 包含所有結果
                'detailed_results': filtered_results,
                'all_results': detailed_results,  # 包含所有結果
                'stats': stats,
                'raw_ocr_result': results
            }
            
        except Exception as e:
            raise Exception(f"圖片處理失敗: {e}")
    
    def save_result_to_file(self, result: Dict, input_file: str, format_type: str = 'txt') -> str:
        """儲存結果到檔案"""
        output_folder = './output'
        os.makedirs(output_folder, exist_ok=True)
        
        base_name = Path(input_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'txt':
            output_path = os.path.join(output_folder, f"{base_name}_{timestamp}_fixed.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== PaddleOCR 處理結果（修復版本）===\n")
                f.write(f"原始檔案: {Path(input_file).name}\n")
                f.write(f"處理時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                stats = result['stats']
                f.write("=== 處理統計 ===\n")
                f.write(f"處理時間: {stats['processing_time']}\n")
                f.write(f"檢測行數: {stats['total_detected']}\n")
                f.write(f"接受行數: {stats['accepted_lines']}\n")
                f.write(f"字符數: {stats['total_chars']}\n")
                f.write(f"詞數: {stats['total_words']}\n")
                f.write(f"信心度閾值: {stats['confidence_threshold']}\n")
                f.write(f"平均信心度: {stats['average_confidence']:.3f}\n\n")
                
                f.write("=== 識別內容（過濾後）===\n")
                f.write(result['text_content'])
                f.write("\n\n")
                
                f.write("=== 詳細結果 ===\n")
                for i, item in enumerate(result['detailed_results']):
                    f.write(f"行 {i+1}: '{item['text']}' (信心度: {item['confidence']:.3f})\n")
                    if item['bbox']:
                        f.write(f"  座標: {item['bbox']}\n")
                    f.write("\n")
                
                if result['all_results'] != result['detailed_results']:
                    f.write("=== 所有檢測結果（包含低信心度）===\n")
                    for i, item in enumerate(result['all_results']):
                        f.write(f"行 {i+1}: '{item['text']}' (信心度: {item['confidence']:.3f})\n")
            
            print(f"✓ 結果已儲存: {output_path}")
            return output_path
        
        elif format_type == 'docx':
            output_path = os.path.join(output_folder, f"{base_name}_{timestamp}_fixed.docx")
            
            doc = docx.Document()
            
            # 設定字體
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Microsoft YaHei'
            font.size = Pt(12)
            
            # 標題
            title = doc.add_heading('PaddleOCR 識別結果', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 檔案資訊
            info_para = doc.add_paragraph()
            info_para.add_run(f"原始檔案: {Path(input_file).name}\n").bold = True
            info_para.add_run(f"處理時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 統計資訊
            stats = result['stats']
            stats_para = doc.add_paragraph()
            stats_para.add_run("處理統計:\n").bold = True
            stats_para.add_run(f"• 處理時間: {stats['processing_time']}\n")
            stats_para.add_run(f"• 檢測行數: {stats['total_detected']}\n")
            stats_para.add_run(f"• 接受行數: {stats['accepted_lines']}\n")
            stats_para.add_run(f"• 字符數: {stats['total_chars']}\n")
            stats_para.add_run(f"• 平均信心度: {stats['average_confidence']:.3f}\n")
            
            # 分隔線
            doc.add_paragraph("=" * 50)
            
            # 識別內容
            content_heading = doc.add_heading('識別內容', level=1)
            
            paragraphs = result['text_content'].split('\n')
            for para_text in paragraphs:
                if para_text.strip():
                    para = doc.add_paragraph(para_text)
                else:
                    doc.add_paragraph()
            
            doc.save(output_path)
            print(f"✓ DOCX 檔案已儲存: {output_path}")
            return output_path
        
        elif format_type == 'pdf':
            output_path = os.path.join(output_folder, f"{base_name}_{timestamp}_fixed.pdf")
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # 嘗試註冊中文字體
            try:
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",
                    "C:/Windows/Fonts/simsun.ttc"
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        styles['Normal'].fontName = 'Chinese'
                        styles['Title'].fontName = 'Chinese'
                        styles['Heading1'].fontName = 'Chinese'
                        break
            except:
                pass
            
            story = []
            
            # 標題
            title = Paragraph("PaddleOCR 識別結果", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 檔案資訊
            stats = result['stats']
            info_text = f"""
            原始檔案: {Path(input_file).name}<br/>
            處理時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            檢測行數: {stats['total_detected']}<br/>
            接受行數: {stats['accepted_lines']}<br/>
            字符數: {stats['total_chars']}<br/>
            平均信心度: {stats['average_confidence']:.3f}
            """
            info_para = Paragraph(info_text, styles['Normal'])
            story.append(info_para)
            story.append(Spacer(1, 20))
            
            # 內容標題
            content_title = Paragraph("識別內容", styles['Heading1'])
            story.append(content_title)
            story.append(Spacer(1, 12))
            
            # 內容
            paragraphs = result['text_content'].split('\n')
            for para_text in paragraphs:
                if para_text.strip():
                    safe_text = para_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    para = Paragraph(safe_text, styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 6))
            
            doc.build(story)
            print(f"✓ PDF 檔案已儲存: {output_path}")
            return output_path
    
    def create_better_test_image(self, text: str = "測試中文 English 123", output_path: str = "better_test.png"):
        """建立更好的測試圖片"""
        img = Image.new('RGB', (1000, 300), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # 嘗試使用更好的字體
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/arial.ttf",
                "arial.ttf"
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 72)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
        
        except:
            font = ImageFont.load_default()
        
        # 計算文字位置（置中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
        
        # 添加背景增強對比度
        padding = 20
        draw.rectangle([x-padding, y-padding//2, x+text_width+padding, y+text_height+padding//2], 
                      fill='white', outline='gray', width=2)
        
        # 繪製文字
        draw.text((x, y), text, font=font, fill='black')
        
        img.save(output_path, 'PNG', quality=95)
        print(f"✓ 測試圖片已建立: {output_path}")
        return output_path
    
    def batch_process_images(self, image_folder: str, confidence_threshold: float = 0.5, output_format: str = 'txt') -> List[str]:
        """批量處理圖片"""
        if not os.path.exists(image_folder):
            raise FileNotFoundError(f"找不到資料夾: {image_folder}")
        
        # 支援的圖片格式
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        image_files = []
        
        for file in os.listdir(image_folder):
            if file.lower().endswith(supported_formats):
                image_files.append(os.path.join(image_folder, file))
        
        if not image_files:
            print("資料夾中沒有找到支援的圖片檔案")
            return []
        
        print(f"找到 {len(image_files)} 個圖片檔案")
        output_files = []
        
        for i, image_file in enumerate(image_files, 1):
            print(f"\n處理第 {i}/{len(image_files)} 個檔案: {os.path.basename(image_file)}")
            
            try:
                result = self.process_image(image_file, confidence_threshold)
                output_file = self.save_result_to_file(result, image_file, output_format)
                output_files.append(output_file)
                
                print(f"✓ 完成，識別 {len(result['text_content'])} 個字符")
                
            except Exception as e:
                print(f"✗ 處理失敗: {e}")
        
        print(f"\n批量處理完成，成功處理 {len(output_files)}/{len(image_files)} 個檔案")
        return output_files


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='修復版 PaddleOCR 處理器')
    parser.add_argument('--file', help='圖片檔案路徑')
    parser.add_argument('--folder', help='圖片資料夾路徑（批量處理）')
    parser.add_argument('--format', choices=['txt', 'docx', 'pdf'], default='txt', help='輸出格式')
    parser.add_argument('--confidence', type=float, default=0.5, help='信心度閾值')
    parser.add_argument('--test', action='store_true', help='建立測試圖片並處理')
    
    args = parser.parse_args()
    
    processor = OptimizedOCRProcessor()
    
    if processor.ocr_engine is None:
        print("OCR 引擎初始化失敗")
        return
    
    if args.test:
        print("建立並測試示例圖片...")
        
        test_images = [
            ("Hello World", "test_fixed_en.png"),
            ("測試中文", "test_fixed_ch.png"),
            ("混合 Mixed 123", "test_fixed_mixed.png")
        ]
        
        for text, filename in test_images:
            print(f"\n處理測試: {text}")
            img_path = processor.create_better_test_image(text, filename)
            
            try:
                result = processor.process_image(img_path, args.confidence)
                output_file = processor.save_result_to_file(result, img_path, args.format)
                
                print(f"✓ 成功處理，識別內容:")
                if result['text_content']:
                    for line in result['text_content'].split('\n'):
                        print(f"  '{line}'")
                else:
                    print("  (無內容)")
                    
            except Exception as e:
                print(f"✗ 處理失敗: {e}")
        
        return
    
    if args.folder:
        try:
            output_files = processor.batch_process_images(args.folder, args.confidence, args.format)
            print(f"\n✓ 批量處理完成，輸出 {len(output_files)} 個檔案")
            
        except Exception as e:
            print(f"批量處理失敗: {e}")
        return
    
    if args.file:
        try:
            result = processor.process_image(args.file, args.confidence)
            output_file = processor.save_result_to_file(result, args.file, args.format)
            
            print(f"\n✓ 處理完成")
            print(f"識別內容:")
            if result['text_content']:
                for line in result['text_content'].split('\n'):
                    print(f"  '{line}'")
            else:
                print("  (無內容)")
            
            print(f"輸出檔案: {output_file}")
            
        except Exception as e:
            print(f"處理失敗: {e}")
        return
    
    # 互動模式
    print("=== 修復版 PaddleOCR 處理器 ===")
    print("1. 建立並測試示例圖片")
    print("2. 處理您的圖片檔案")
    print("3. 批量處理圖片資料夾")
    print("4. 退出")
    
    while True:
        choice = input("\n請選擇操作 (1-4): ").strip()
        
        if choice == '1':
            test_images = [
                ("Hello World", "test_fixed_en.png"),
                ("測試中文識別", "test_fixed_ch.png"),
                ("Mixed 混合內容 123", "test_fixed_mixed.png")
            ]
            
            format_choice = input("選擇輸出格式 (txt/docx/pdf, 預設 txt): ").strip() or 'txt'
            
            for text, filename in test_images:
                print(f"\n處理測試: {text}")
                img_path = processor.create_better_test_image(text, filename)
                
                try:
                    result = processor.process_image(img_path, 0.5)
                    output_file = processor.save_result_to_file(result, img_path, format_choice)
                    
                    print(f"✓ 識別內容: '{result['text_content']}'")
                    
                except Exception as e:
                    print(f"✗ 處理失敗: {e}")
        
        elif choice == '2':
            file_path = input("請輸入圖片檔案路徑: ").strip().strip('"')
            if os.path.exists(file_path):
                format_choice = input("選擇輸出格式 (txt/docx/pdf, 預設 txt): ").strip() or 'txt'
                confidence = input("信心度閾值 (0.0-1.0, 預設 0.5): ").strip()
                confidence = float(confidence) if confidence else 0.5
                
                try:
                    result = processor.process_image(file_path, confidence)
                    output_file = processor.save_result_to_file(result, file_path, format_choice)
                    
                    print(f"✓ 處理完成，識別內容:")
                    if result['text_content']:
                        for line in result['text_content'].split('\n'):
                            print(f"  '{line}'")
                    else:
                        print("  (無內容)")
                    
                except Exception as e:
                    print(f"處理失敗: {e}")
            else:
                print("檔案不存在")
        
        elif choice == '3':
            folder_path = input("請輸入圖片資料夾路徑: ").strip().strip('"')
            if os.path.exists(folder_path):
                format_choice = input("選擇輸出格式 (txt/docx/pdf, 預設 txt): ").strip() or 'txt'
                confidence = input("信心度閾值 (0.0-1.0, 預設 0.5): ").strip()
                confidence = float(confidence) if confidence else 0.5
                
                try:
                    output_files = processor.batch_process_images(folder_path, confidence, format_choice)
                    print(f"✓ 批量處理完成，輸出 {len(output_files)} 個檔案")
                    
                except Exception as e:
                    print(f"批量處理失敗: {e}")
            else:
                print("資料夾不存在")
        
        elif choice == '4':
            print("退出程式")
            break
        
        else:
            print("無效的選擇")


if __name__ == "__main__":
    main()