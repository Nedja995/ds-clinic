# redaction_worker.py
import os
import time
import threading
import numpy as np
from PIL import Image, ImageDraw
import easyocr
import spacy
import fitz  # PyMuPDF
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine

class EasyOCRAdapter:
    """Adapts EasyOCR to handle multi-script setups sequentially without crashing."""
    def __init__(self, output_queue=None):
        self.output_queue = output_queue
        loading_done_event = threading.Event()
        
        if self.output_queue:
            timeout_thread = threading.Thread(
                target=self._delayed_download_notifier, 
                args=(loading_done_event,), 
                daemon=True
            )
            timeout_thread.start()

        self.reader_latin = easyocr.Reader(['en', 'rs_latin'], gpu=False)
        self.reader_cyrillic = easyocr.Reader(['en', 'rs_cyrillic'], gpu=False)
        loading_done_event.set()

    def _delayed_download_notifier(self, loading_done_event: threading.Event):
        time.sleep(1.5)
        if not loading_done_event.is_set():
            self.output_queue.put({
                "status": "DOWNLOADING_MODELS", 
                "message": "Initializing local privacy layers...."#"Downloading Serbian & English OCR language modules (First-time run only)..."
            })

    def perform_ocr(self, image: Image.Image):
        img_array = np.array(image)
        results = self.reader_latin.readtext(img_array)
        if len(results) == 0:
            results = self.reader_cyrillic.readtext(img_array)
            
        ocr_data = []
        for (bbox, text, prob) in results:
            x_coords = [int(point[0]) for point in bbox]
            y_coords = [int(point[1]) for point in bbox]
            
            ocr_data.append({
                "text": str(text).strip(),
                "left": min(x_coords),
                "top": min(y_coords),
                "width": max(1, max(x_coords) - min(x_coords)),
                "height": max(1, max(y_coords) - min(y_coords))
            })
        return ocr_data


def process_and_redact_image(img, ocr_engine, analyzer):
    """Your existing, proven image-scrubbing logic isolated into a clean helper function."""
    ocr_words = ocr_engine.perform_ocr(img)
    
    full_text = ""
    word_positions = []
    for word in ocr_words:
        start_idx = len(full_text)
        full_text += word["text"] + " "
        end_idx = len(full_text) - 1
        word_positions.append((start_idx, end_idx, word))
    
    analysis_results = analyzer.analyze(
        text=full_text, 
        language="en", 
        entities=["PERSON", "LOCATION", "SR_JMBG"]
    )
    
    draw = ImageDraw.Draw(img)
    for result in analysis_results:
        for start, end, word in word_positions:
            if not (end <= result.start or start >= result.end):
                x1, y1 = word["left"], word["top"]
                x2, y2 = x1 + word["width"], y1 + word["height"]
                draw.rectangle([x1 - 2, y1 - 2, x2 + 2, y2 + 2], fill="black")
    return img


def redaction_worker_process(input_queue, output_queue):
    """Isolated process running the unified image & PDF image-conversion engine."""
    ocr_engine = EasyOCRAdapter(output_queue=output_queue)
    anonymizer = AnonymizerEngine()
    
    # Custom rules setups
    jmbg_pattern = Pattern(name="jmbg_regex", regex=r"\b\d{13}\b", score=0.85)
    jmbg_recognizer = PatternRecognizer(supported_entity="SR_JMBG", supported_language="sr", patterns=[jmbg_pattern])
    jmbg_recognizer.context_words = ["jmbg", "matični", "broj", "јмбг", "матиčni"]
    
    name_header_pattern = Pattern(
        name="name_field_regex", 
        regex=r"(?i)(?:name|ime|pacijent|patient)\s*[:.-]?\s*([A-ZŽĆČĐŠ][a-zžćčđš]+(?:\s+[A-ZŽĆČĐŠ][a-zžćčđš]+)+)", 
        score=0.95
    )
    name_field_recognizer = PatternRecognizer(supported_entity="PERSON", supported_language="en", patterns=[name_header_pattern])
    
    nlp_model = spacy.load("en_core_web_sm")
    spacy_engine = SpacyNlpEngine()
    spacy_engine.nlp = {"en": nlp_model}
    
    analyzer = AnalyzerEngine(nlp_engine=spacy_engine)
    analyzer.registry.add_recognizer(jmbg_recognizer)
    analyzer.registry.add_recognizer(name_field_recognizer)

    while True:
        task = input_queue.get()
        if task is None:
            break
            
        input_path = task.get("input_path")
        output_path = task.get("output_path")
        
        try:
            # ── UNIFIED PDF PIPELINE (Converts pages to images) ──────────────────
            if input_path.lower().endswith('.pdf'):
                doc = fitz.open(input_path)
                
                # If it's a multi-page PDF, we'll save pages as separate files for Gemini
                base_out, _ = os.path.splitext(output_path)
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    # Render page to a high-res image matrix (matrix zoom level 2.0 = sharp text recognition)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Run your identical image scrubbing logic!
                    scrubbed_img = process_and_redact_image(img, ocr_engine, analyzer)
                    
                    # Save pages dynamically as page_0.jpg, page_1.jpg etc.
                    page_output_path = f"{base_out}_page_{page_num}.jpg"
                    scrubbed_img.save(page_output_path, "JPEG", quality=90)
                
                doc.close()
                output_queue.put({"status": "SUCCESS", "output_path": output_path})
                continue
            # ──────────────────────────────────────────────────────────────────
            
            # Standard single image file workflow
            img = Image.open(input_path).convert("RGB")
            scrubbed_img = process_and_redact_image(img, ocr_engine, analyzer)
            scrubbed_img.save(output_path)
            
            output_queue.put({"status": "SUCCESS", "output_path": output_path})
                
        except Exception as e:
            output_queue.put({"status": "ERROR", "error_message": str(e)})
