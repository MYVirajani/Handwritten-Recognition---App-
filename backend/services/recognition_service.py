import time
import logging
from PIL import Image
import io
import numpy as np
import cv2
import fitz  
from typing import List, Tuple
import re

logger = logging.getLogger(__name__)


try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TROCR_AVAILABLE = True
    logger.info("✓ TrOCR imports successful")
except ImportError as e:
    logger.error(f"✗ TrOCR import failed: {e}")
    TROCR_AVAILABLE = False

class RecognitionService:
    def __init__(self):
        """Initialize TrOCR models for handwriting recognition"""
        self.trocr_loaded = False
        
        if TROCR_AVAILABLE:
            try:
                logger.info("Loading TrOCR models...")
                self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                logger.info(f"Using device: {self.device}")
                
                
                logger.info("Loading handwritten text model...")
                self.processor_hw = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
                self.model_hw = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten').to(self.device)
                
                
                logger.info("Loading printed text model...")
                self.processor_pr = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
                self.model_pr = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed').to(self.device)
                
                self.trocr_loaded = True
                logger.info("✓ TrOCR models loaded successfully!")
            except Exception as e:
                logger.error(f"✗ Error loading TrOCR: {e}")
                import traceback
                traceback.print_exc()
                self.trocr_loaded = False
    
    def recognize(self, file_path, file_type):
        """Main recognition method - PDF ONLY"""
        start_time = time.time()
        
        try:
            if not self.trocr_loaded:
                return {
                    'success': False,
                    'error': 'TrOCR model not available'
                }
            
            
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            
            if file_type != 'pdf':
                return {
                    'success': False,
                    'error': 'Only PDF files are accepted'
                }
            
            
            logger.info("Converting PDF to images...")
            page_images = self.pdf_to_images(file_bytes, dpi=350)
            
            if not page_images:
                return {
                    'success': False,
                    'error': 'Failed to extract pages from PDF. The PDF might be corrupted or empty.'
                }
            
            
            all_pages_text = []
            total_confidence = 0
            total_lines = 0
            
            for page_num, img in enumerate(page_images):
                logger.info(f"Processing page/image {page_num + 1}...")
                
                if img is None:
                    continue
                
                
                enhanced_img = self.advanced_image_preprocessing(img)
                if enhanced_img is None:
                    continue
                
                
                text_regions = self.detect_actual_text_regions(enhanced_img)
                logger.info(f"Page {page_num + 1}: Detected {len(text_regions)} text regions")
                
                page_text_lines = []
                line_confidences = []
                
                
                for i, region in enumerate(text_regions):
                    line_img = self.preprocess_line_for_ocr(enhanced_img, region)
                    
                    if line_img is not None:
                        line_text, line_conf = self.extract_text_single_line(line_img, i+1)
                        
                        if line_text.strip():
                            page_text_lines.append(line_text)
                            line_confidences.append(line_conf)
                            total_lines += 1
                
                
                page_text = '\n'.join(page_text_lines)
                all_pages_text.append(page_text)
                
                
                page_confidence = np.mean(line_confidences) if line_confidences else 0.0
                total_confidence += page_confidence
            
            
            final_text = self.format_extracted_text(all_pages_text)
            
            
            overall_confidence = total_confidence / len(page_images) if page_images else 0.0
            
            processing_time = time.time() - start_time
            
            if not final_text.strip():
                return {
                    'success': False,
                    'error': 'No readable text found in the document'
                }
            
            return {
                'success': True,
                'text': final_text,
                'confidence': round(overall_confidence, 3),
                'processing_time': round(processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def load_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """Load image from bytes and convert to numpy array"""
        try:
            logger.info(f"Loading image from {len(image_bytes)} bytes...")
            
            if len(image_bytes) == 0:
                logger.error("Image bytes are empty")
                return None
            
            
            image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"PIL Image loaded: {image.mode}, size: {image.size}")
            
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            
            img_array = np.array(image)
            logger.info(f"Numpy array shape: {img_array.shape}")
            
            return img_array
        except Exception as e:
            logger.error(f"Error loading image from bytes: {e}")
            return None
    
    def pdf_to_images(self, pdf_bytes: bytes, dpi: int = 350) -> List[np.ndarray]:
        """Convert PDF pages to high-resolution images"""
        images = []
        try:
            logger.info(f"Converting PDF ({len(pdf_bytes)} bytes) to images at {dpi} DPI...")
            
            if len(pdf_bytes) == 0:
                logger.error("PDF bytes are empty")
                return []
            
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            logger.info(f"PDF opened successfully, {len(pdf_document)} pages")
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    images.append(img)
                    logger.info(f"✓ PDF page {page_num + 1} converted")
            
            pdf_document.close()
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []
    
    def advanced_image_preprocessing(self, img: np.ndarray) -> np.ndarray:
        """Minimal preprocessing to preserve handwriting quality"""
        if img is None:
            return None
        
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        denoised = cv2.medianBlur(gray, 3)
        clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def detect_actual_text_regions(self, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect text regions in the image"""
        if img is None:
            return []
        
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
        h, w = gray.shape
        
        
        _, binary1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 21, 8)
        
        mean_brightness = np.mean(gray)
        threshold_val = max(120, min(180, mean_brightness - 30))
        _, binary3 = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)
        
        
        combined_binary = np.zeros_like(binary1)
        for y in range(h):
            for x in range(w):
                votes = sum(1 for binary in [binary1, binary2, binary3] if binary[y, x] > 0)
                if votes >= 2:
                    combined_binary[y, x] = 255
        
        
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        combined_binary = cv2.morphologyEx(combined_binary, cv2.MORPH_OPEN, kernel_clean)
        
        
        contours, _ = cv2.findContours(combined_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= 25:
                x, y, w_c, h_c = cv2.boundingRect(contour)
                if w_c >= 10 and h_c >= 5:
                    valid_contours.append((x, y, x + w_c, y + h_c))
        
        if valid_contours:
            text_regions = self._group_contours_into_lines(valid_contours, h, w)
        else:
            text_regions = []
        
        return text_regions
    
    def _group_contours_into_lines(self, contours, img_h, img_w):
        """Group contours into text lines"""
        if not contours:
            return []
        
        contours = sorted(contours, key=lambda x: x[1])
        lines = []
        current_line = [contours[0]]
        
        for i in range(1, len(contours)):
            curr = contours[i]
            prev = contours[i-1]
            
            vertical_gap = curr[1] - prev[3]
            
            if vertical_gap > 5:  
                line_bbox = self._merge_contours(current_line, img_w, img_h)
                if line_bbox:
                    lines.append(line_bbox)
                current_line = [curr]
            else:
                current_line.append(curr)
        
        if current_line:
            line_bbox = self._merge_contours(current_line, img_w, img_h)
            if line_bbox:
                lines.append(line_bbox)
        
        return lines
    
    def _merge_contours(self, contours, img_w, img_h):
        """Merge contours into a single bounding box"""
        if not contours:
            return None
        
        min_x = min(c[0] for c in contours)
        min_y = min(c[1] for c in contours)
        max_x = max(c[2] for c in contours)
        max_y = max(c[3] for c in contours)
        
        x1 = max(0, min_x - 8)
        y1 = max(0, min_y - 4)
        x2 = min(img_w, max_x + 8)
        y2 = min(img_h, max_y + 4)
        
        if (x2 - x1) < 15 or (y2 - y1) < 6:
            return None
        
        return (x1, y1, x2, y2)
    
    def preprocess_line_for_ocr(self, img: np.ndarray, line_box: Tuple[int, int, int, int]) -> np.ndarray:
        """Prepare line image for OCR"""
        x1, y1, x2, y2 = line_box
        line_img = img[y1:y2, x1:x2].copy()
        
        if line_img.size == 0:
            return None
        
        if len(line_img.shape) == 3:
            line_img = cv2.cvtColor(line_img, cv2.COLOR_RGB2GRAY)
        
        line_img = cv2.normalize(line_img, None, 0, 255, cv2.NORM_MINMAX)
        
        height, width = line_img.shape
        target_height = 32 if height < 20 else (80 if height > 120 else height)
        
        if height != target_height:
            scale = target_height / height
            new_width = max(int(width * scale), 64)
            new_width = min(new_width, 800)
            line_img = cv2.resize(line_img, (new_width, target_height), 
                                interpolation=cv2.INTER_CUBIC)
        
        line_img = cv2.copyMakeBorder(line_img, 8, 8, 12, 12, 
                                    cv2.BORDER_CONSTANT, value=255)
        
        if np.mean(line_img) < 128:
            line_img = cv2.bitwise_not(line_img)
        
        line_img_rgb = cv2.cvtColor(line_img, cv2.COLOR_GRAY2RGB)
        
        return line_img_rgb
    
    def extract_text_single_line(self, line_img, line_number, model_type='handwritten'):
        """Extract text from a single line using TrOCR"""
        if line_img is None or not self.trocr_loaded:
            return "", 0.0
        
        processor = self.processor_hw if model_type == 'handwritten' else self.processor_pr
        model = self.model_hw if model_type == 'handwritten' else self.model_pr
        
        try:
            pil_img = Image.fromarray(line_img)
            
            pixel_values = processor(pil_img, return_tensors="pt").pixel_values.to(self.device)
            
            with torch.no_grad():
                generated_ids = model.generate(
                    pixel_values,
                    max_length=80,
                    num_beams=2,
                    early_stopping=True,
                    do_sample=False,
                    length_penalty=1.2,
                    repetition_penalty=1.2
                )
            
            text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            text = self.clean_extracted_text(text)
            
            if text.strip() and len(text.strip()) >= 2:
                confidence = self.calculate_text_confidence(text)
                
                if confidence > 0.15:
                    return text, confidence
                else:
                    if self._has_recognizable_patterns(text):
                        return text, 0.25
                    else:
                        return "", 0.0
            
            return "", 0.0
                    
        except Exception as e:
            logger.error(f"Error processing line {line_number}: {e}")
            return "", 0.0
    
    def _has_recognizable_patterns(self, text: str) -> bool:
        """Identify potentially valid text patterns"""
        if not text or len(text.strip()) < 2:
            return False
        
        text_clean = text.strip().lower()
        
        patterns = [
            r'^q\d+',
            r'^\(\s*[ivx]+\s*\)',
            r'^\d+[\.\):]',
            r'^[a-z]+\s+[a-z]+',
            r'\d+',
            r'[aeiou]',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_clean):
                return True
        
        alpha_chars = sum(1 for c in text_clean if c.isalpha())
        return alpha_chars >= 2
    
    def clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        text = text.strip()
        text = ' '.join(text.split())
        
        if len(text.strip()) < 2:
            return ""
        
        if len(set(text.replace(' ', ''))) <= 1 and len(text) > 3:
            return ""
        
        
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence score for extracted text"""
        if not text or len(text.strip()) < 2:
            return 0.0
        
        text_clean = text.strip()
        char_count = len(text_clean)
        
        
        if char_count < 3:
            length_score = 0.6
        elif 3 <= char_count <= 80:
            length_score = 1.0
        else:
            length_score = 0.8
        
        
        alpha_chars = sum(1 for c in text_clean if c.isalpha())
        digit_chars = sum(1 for c in text_clean if c.isdigit())
        space_chars = sum(1 for c in text_clean if c.isspace())
        punct_chars = sum(1 for c in text_clean if c in '.,!?;:()-\'\"')
        
        meaningful_chars = alpha_chars + digit_chars + space_chars + punct_chars
        char_ratio = meaningful_chars / char_count if char_count > 0 else 0
        
       
        words = text_clean.split()
        word_score = 0.5
        if words:
            valid_words = sum(1 for word in words if len(word) >= 2)
            word_score = valid_words / len(words) if words else 0.5
        
        
        final_confidence = (
            length_score * 0.25 +
            char_ratio * 0.25 +
            word_score * 0.4 +
            0.1
        )
        
        return min(1.0, max(0.0, final_confidence))
    
    def format_extracted_text(self, pages_text: List[str]) -> str:
        """Format extracted text from multiple pages"""
        formatted_output = []
        
        for page_text in pages_text:
            if not page_text.strip():
                continue
            
            lines = page_text.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    formatted_output.append(line)
        
        return '\n'.join(formatted_output)