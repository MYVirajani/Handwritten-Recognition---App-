from database import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

class Upload:
    @staticmethod
    def create(filename, file_path, file_type, file_size):
        """Create a new upload record"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO uploads (filename, file_path, file_type, file_size)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (filename, file_path, file_type, file_size))
            
            upload_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Upload record created with ID: {upload_id}")
            return upload_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating upload record: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()
                return_db_connection(conn)
    
    @staticmethod
    def get_by_id(upload_id):
        """Get upload by ID"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM uploads WHERE id = %s
            """, (upload_id,))
            
            return cursor.fetchone()
            
        except Exception as e:
            logger.error(f"Error fetching upload: {str(e)}")
            return None
        finally:
            if conn:
                cursor.close()
                return_db_connection(conn)

class RecognitionResult:
    @staticmethod
    def create(upload_id, recognized_text, confidence_score=None, processing_time=None):
        """Create a new recognition result record"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO recognition_results 
                (upload_id, recognized_text, confidence_score, processing_time)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (upload_id, recognized_text, confidence_score, processing_time))
            
            result_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Recognition result created with ID: {result_id}")
            return result_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating recognition result: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()
                return_db_connection(conn)
    
    @staticmethod
    def get_by_upload_id(upload_id):
        """Get recognition result by upload ID"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM recognition_results 
                WHERE upload_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (upload_id,))
            
            return cursor.fetchone()
            
        except Exception as e:
            logger.error(f"Error fetching recognition result: {str(e)}")
            return None
        finally:
            if conn:
                cursor.close()
                return_db_connection(conn)