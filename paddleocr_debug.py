# paddleocr_debug.py
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 核心套件
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("警告: PaddleOCR 未安裝")


class PaddleOCRDiagnostic:
    """PaddleOCR 診斷工具"""
    
    def __init__(self):
        self.ocr_engine = None
        self.test_images = []
        
    def check_environment(self):
        """檢查環境配置"""
        print("=== 環境檢查 ===")
        
        # Python 版本
        print(f"Python 版本: {sys.version}")
        
        # 套件檢查
        packages = [
            'paddlepaddle',
            'paddleocr', 
            'opencv-python',
            'pillow',
            'numpy'
        ]
        
        for package in packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✓ {package}: 已安裝")
            except ImportError:
                print(f"✗ {package}: 未安裝")
        
        # PaddleOCR 可用性
        if PADDLEOCR_AVAILABLE:
            print("✓ PaddleOCR: 可用")
        else:
            print("✗ PaddleOCR: 不可用")
            
        return PADDLEOCR_AVAILABLE
    
    def test_ocr_initialization(self):
        """測試 OCR 初始化"""
        print("\n=== OCR 初始化測試 ===")
        
        if not PADDLEOCR_AVAILABLE:
            print("PaddleOCR 不可用，跳過測試")
            return False
        
        configs = [
            {'lang': 'ch'},
            {'lang': 'en'},
            {'lang': 'ch', 'use_angle_cls': True},
            {'lang': 'en', 'use_angle_cls': True},
        ]
        
        for i, config in enumerate(configs):
            print(f"\n測試配置 {i+1}: {config}")
            try:
                start_time = time.time()
                ocr = PaddleOCR(**config)
                init_time = time.time() - start_time
                
                print(f"✓ 初始化成功，耗時: {init_time:.2f} 秒")
                
                if self.ocr_engine is None:
                    self.ocr_engine = ocr
                    self.current_config = config
                    print("✓ 設為預設引擎")
                
                return True
                
            except Exception as e:
                print(f"✗ 初始化失敗: {e}")
        
        return False
    
    def create_test_images(self):
        """建立測試圖片"""
        print("\n=== 建立測試圖片 ===")
        
        test_cases = [
            ("Hello", "english_simple"),
            ("Hello World", "english_phrase"),
            ("123456", "numbers"),
            ("測試", "chinese_simple"),
            ("測試中文", "chinese_phrase"),
            ("Mixed 混合 123", "mixed_content"),
            ("ABCDEFG\n1234567", "multiline"),
        ]
        
        os.makedirs("./test_examples", exist_ok=True)
        
        for text, name in test_cases:
            filename = f"./test_examples/test_{name}.png"
            
            try:
                img = Image.new('RGB', (800, 200), 'white')
                draw = ImageDraw.Draw(img)
                
                # 嘗試載入字體
                font = None
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",
                    "C:/Windows/Fonts/arial.ttf",
                    "/System/Library/Fonts/Arial.ttf",
                    "arial.ttf"
                ]
                
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, 48)
                        break
                    except:
                        continue
                
                if font is None:
                    font = ImageFont.load_default()
                
                # 計算文字位置
                if '\n' in text:
                    lines = text.split('\n')
                    y_start = 50
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                        x = (img.width - text_width) // 2
                        draw.text((x, y_start), line, font=font, fill='black')
                        y_start += 60
                else:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (img.width - text_width) // 2
                    y = (img.height - text_height) // 2
                    draw.text((x, y), text, font=font, fill='black')
                
                img.save(filename, 'PNG')
                self.test_images.append((filename, text))
                print(f"✓ 建立: {filename}")
                
            except Exception as e:
                print(f"✗ 建立失敗 {filename}: {e}")
    
    def test_ocr_recognition(self):
        """測試 OCR 識別"""
        print("\n=== OCR 識別測試 ===")
        
        if self.ocr_engine is None:
            print("OCR 引擎未初始化")
            return
        
        if not self.test_images:
            print("沒有測試圖片")
            return
        
        results = []
        
        for image_path, expected_text in self.test_images:
            print(f"\n測試圖片: {os.path.basename(image_path)}")
            print(f"預期文字: '{expected_text}'")
            
            try:
                start_time = time.time()
                
                # 嘗試不同的調用方法
                try:
                    ocr_result = self.ocr_engine.predict(image_path)
                except AttributeError:
                    ocr_result = self.ocr_engine.ocr(image_path)
                
                process_time = time.time() - start_time
                
                # 解析結果
                recognized_text = self._extract_text_from_result(ocr_result)
                
                print(f"識別文字: '{recognized_text}'")
                print(f"處理時間: {process_time:.2f} 秒")
                
                # 簡單的準確度評估
                if recognized_text.strip():
                    if expected_text.lower() in recognized_text.lower() or recognized_text.lower() in expected_text.lower():
                        accuracy = "✓ 良好"
                    else:
                        accuracy = "△ 部分"
                else:
                    accuracy = "✗ 失敗"
                
                print(f"準確度: {accuracy}")
                
                results.append({
                    'image': image_path,
                    'expected': expected_text,
                    'recognized': recognized_text,
                    'time': process_time,
                    'success': accuracy.startswith('✓')
                })
                
            except Exception as e:
                print(f"✗ 識別失敗: {e}")
                results.append({
                    'image': image_path,
                    'expected': expected_text,
                    'recognized': '',
                    'time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _extract_text_from_result(self, result):
        """從 OCR 結果中提取文字"""
        text_lines = []
        
        try:
            if isinstance(result, list) and len(result) > 0:
                ocr_result = result[0]
                
                # 新版 API
                if hasattr(ocr_result, 'rec_texts') and ocr_result.rec_texts:
                    text_lines.extend(ocr_result.rec_texts)
                
                # 舊版 API 兼容
                elif isinstance(ocr_result, dict) and 'rec_texts' in ocr_result:
                    text_lines.extend(ocr_result['rec_texts'])
                
                # 傳統格式
                elif isinstance(result, list):
                    for line in result:
                        if isinstance(line, list) and len(line) >= 2:
                            text_lines.append(line[1][0])
        
        except Exception as e:
            print(f"結果解析錯誤: {e}")
        
        return '\n'.join(text_lines)
    
    def generate_report(self, results):
        """生成診斷報告"""
        print("\n" + "="*50)
        print("=== PaddleOCR 診斷報告 ===")
        print("="*50)
        
        if not results:
            print("沒有測試結果")
            return
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        success_rate = (successful / total) * 100
        
        print(f"總測試數: {total}")
        print(f"成功數: {successful}")
        print(f"成功率: {success_rate:.1f}%")
        
        if successful > 0:
            avg_time = sum(r['time'] for r in results if r['success']) / successful
            print(f"平均處理時間: {avg_time:.2f} 秒")
        
        print("\n=== 詳細結果 ===")
        for i, result in enumerate(results, 1):
            print(f"\n測試 {i}: {os.path.basename(result['image'])}")
            print(f"  預期: '{result['expected']}'")
            print(f"  識別: '{result['recognized']}'")
            print(f"  時間: {result['time']:.2f} 秒")
            print(f"  狀態: {'✓ 成功' if result['success'] else '✗ 失敗'}")
            
            if 'error' in result:
                print(f"  錯誤: {result['error']}")
        
        # 建議
        print("\n=== 建議 ===")
        if success_rate >= 80:
            print("✓ OCR 系統運行良好")
        elif success_rate >= 50:
            print("△ OCR 系統部分正常，建議檢查圖片品質或調整參數")
        else:
            print("✗ OCR 系統存在問題，建議重新安裝或檢查環境")
        
        # 儲存報告
        self._save_report(results)
    
    def _save_report(self, results):
        """儲存診斷報告"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'python_version': sys.version,
                'paddleocr_available': PADDLEOCR_AVAILABLE
            },
            'config': getattr(self, 'current_config', None),
            'results': results
        }
        
        os.makedirs('./output', exist_ok=True)
        report_file = f"./output/ocr_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 診斷報告已儲存: {report_file}")
    
    def run_full_diagnostic(self):
        """執行完整診斷"""
        print("PaddleOCR 完整診斷開始...")
        print("="*50)
        
        # 環境檢查
        if not self.check_environment():
            print("\n環境檢查失敗，無法繼續")
            return
        
        # OCR 初始化
        if not self.test_ocr_initialization():
            print("\nOCR 初始化失敗，無法繼續")
            return
        
        # 建立測試圖片
        self.create_test_images()
        
        # OCR 識別測試
        results = self.test_ocr_recognition()
        
        # 生成報告
        self.generate_report(results)
        
        print("\n診斷完成！")


def main():
    """主函數"""
    diagnostic = PaddleOCRDiagnostic()
    
    print("PaddleOCR 診斷工具")
    print("1. 完整診斷")
    print("2. 環境檢查")
    print("3. OCR 初始化測試")
    print("4. 建立測試圖片")
    print("5. OCR 識別測試")
    print("6. 退出")
    
    while True:
        choice = input("\n請選擇操作 (1-6): ").strip()
        
        if choice == '1':
            diagnostic.run_full_diagnostic()
        elif choice == '2':
            diagnostic.check_environment()
        elif choice == '3':
            diagnostic.test_ocr_initialization()
        elif choice == '4':
            diagnostic.create_test_images()
        elif choice == '5':
            if diagnostic.ocr_engine is None:
                print("請先初始化 OCR 引擎（選項 3）")
            else:
                results = diagnostic.test_ocr_recognition()
                if results:
                    diagnostic.generate_report(results)
        elif choice == '6':
            print("退出診斷工具")
            break
        else:
            print("無效選擇")


if __name__ == "__main__":
    main()