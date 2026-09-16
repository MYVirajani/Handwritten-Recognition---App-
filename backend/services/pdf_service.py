from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import os
import logging
import tempfile

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        """Initialize PDF service"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor='#667eea',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor='#666666',
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            textColor='#333333',
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, text):
        """
        Generate PDF from recognized text.
        
        Args:
            text (str): Recognized text to include in PDF
        
        Returns:
            str: Path to generated PDF file
        """
        try:
            
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.pdf',
                prefix='recognized_text_'
            )
            pdf_path = temp_file.name
            temp_file.close()
            
            
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            
            story = []
            
            
            title = Paragraph(
                "Handwritten Text Recognition Result",
                self.styles['CustomTitle']
            )
            story.append(title)
            story.append(Spacer(1, 12))
            
            
            date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            subtitle = Paragraph(
                f"Generated on {date_str}",
                self.styles['CustomSubtitle']
            )
            story.append(subtitle)
            story.append(Spacer(1, 20))
            
            
            from reportlab.platypus import HRFlowable
            story.append(HRFlowable(
                width="100%",
                thickness=1,
                color='#667eea',
                spaceBefore=10,
                spaceAfter=20
            ))
            
            
            paragraphs = text.split('\n')
            
            for para in paragraphs:
                if para.strip():  
                    
                    escaped_text = self._escape_text(para.strip())
                    p = Paragraph(escaped_text, self.styles['CustomBody'])
                    story.append(p)
                else:
                    
                    story.append(Spacer(1, 6))
            
            
            doc.build(story)
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
            raise
    
    def _escape_text(self, text):
        """
        Escape special characters for PDF generation.
        
        Args:
            text (str): Text to escape
        
        Returns:
            str: Escaped text
        """
        
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        return text
    
    def generate_pdf_with_images(self, text, image_paths=None):
        """
        Generate PDF with both text and original images (optional).
        
        Args:
            text (str): Recognized text
            image_paths (list): List of paths to original images
        
        Returns:
            str: Path to generated PDF file
        """
        try:
            
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.pdf',
                prefix='recognized_text_with_images_'
            )
            pdf_path = temp_file.name
            temp_file.close()
            
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            
            title = Paragraph(
                "Handwritten Text Recognition Result",
                self.styles['CustomTitle']
            )
            story.append(title)
            story.append(Spacer(1, 20))
            
            
            if image_paths:
                from reportlab.platypus import Image as RLImage
                
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        img = RLImage(img_path, width=4*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 20))
            
            
            story.append(Paragraph("Recognized Text:", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            paragraphs = text.split('\n')
            for para in paragraphs:
                if para.strip():
                    escaped_text = self._escape_text(para.strip())
                    p = Paragraph(escaped_text, self.styles['CustomBody'])
                    story.append(p)
            
            doc.build(story)
            
            logger.info(f"PDF with images generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF with images: {str(e)}")
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
            raise