from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import Config
from models import Upload, RecognitionResult
from services.recognition_service import RecognitionService
from services.pdf_service import PDFService
import os
import logging

logger = logging.getLogger(__name__)

recognition_bp = Blueprint('recognition', __name__)
recognition_service = RecognitionService()
pdf_service = PDFService()

@recognition_bp.route('/recognize', methods=['POST'])
def recognize_text():
    """Handle PDF upload and text recognition using TrOCR"""
    try:
        
        if 'file' not in request.files:
            logger.error("No file provided in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        
        if not Config.allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
        
        
        if not file.filename.lower().endswith('.pdf'):
            logger.error(f"File does not have .pdf extension: {file.filename}")
            return jsonify({'error': 'Only PDF files are accepted'}), 400
        
        
        filename = secure_filename(file.filename)
        logger.info(f"Processing PDF file: {filename}")
        
        
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        
        file_size = os.path.getsize(file_path)
        file_type = 'pdf'
        
        logger.info(f"PDF uploaded: {filename} ({file_size} bytes)")
        
        
        if not recognition_service.trocr_loaded:
            
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': 'TrOCR model not loaded. Please restart the server.'}), 500
        
        
        try:
            upload_id = Upload.create(
                filename=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size
            )
            logger.info(f"Upload record created with ID: {upload_id}")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            upload_id = None  
        
        
        logger.info("Starting PDF text recognition...")
        result = recognition_service.recognize(file_path, file_type)
        
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temporary PDF file deleted: {filename}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file: {str(e)}")
        
        if result['success']:
            logger.info(f"Recognition successful. Text length: {len(result['text'])} characters")
            
            
            if upload_id:
                try:
                    RecognitionResult.create(
                        upload_id=upload_id,
                        recognized_text=result['text'],
                        confidence_score=result.get('confidence'),
                        processing_time=result.get('processing_time')
                    )
                except Exception as db_error:
                    logger.warning(f"Failed to save recognition result: {db_error}")
            
            return jsonify({
                'success': True,
                'recognized_text': result['text'],
                'confidence': result.get('confidence'),
                'processing_time': result.get('processing_time'),
                'upload_id': upload_id
            }), 200
        else:
            logger.error(f"Recognition failed: {result.get('error')}")
            return jsonify({
                'error': result.get('error', 'Recognition failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in recognize_text: {str(e)}")
        import traceback
        traceback.print_exc()
        
        
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@recognition_bp.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF from recognized text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is empty'}), 400
        
        logger.info(f"Generating PDF for text of length: {len(text)}")
        
        
        pdf_path = pdf_service.generate_pdf(text)
        
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"PDF generated successfully: {pdf_path}")
            
        
            response = send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'recognized_text_{os.path.basename(pdf_path)}'
            )
            
            
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                        logger.info(f"PDF file deleted: {pdf_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete PDF file: {str(e)}")
            
            return response
        else:
            logger.error("Failed to generate PDF")
            return jsonify({'error': 'Failed to generate PDF'}), 500
            
    except Exception as e:
        logger.error(f"Error in download_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@recognition_bp.route('/model-status', methods=['GET'])
def model_status():
    """Check TrOCR model loading status"""
    try:
        status = {
            'trocr_loaded': recognition_service.trocr_loaded,
            'device': str(recognition_service.device) if recognition_service.trocr_loaded else 'N/A',
            'models': {
                'handwritten': recognition_service.trocr_loaded,
                'printed': recognition_service.trocr_loaded
            },
            'accepted_files': ['PDF only']
        }
        logger.info(f"Model status checked: {status}")
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error checking model status: {e}")
        return jsonify({'error': str(e)}), 500