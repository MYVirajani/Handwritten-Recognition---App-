
DROP TABLE IF EXISTS recognition_results CASCADE;
DROP TABLE IF EXISTS uploads CASCADE;


CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL DEFAULT 'pdf',
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_file_type CHECK (file_type = 'pdf')
);


CREATE TABLE recognition_results (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER NOT NULL,
    recognized_text TEXT NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_upload
        FOREIGN KEY (upload_id)
        REFERENCES uploads(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_uploads_upload_date ON uploads(upload_date DESC);
CREATE INDEX idx_uploads_file_type ON uploads(file_type);
CREATE INDEX idx_recognition_results_upload_id ON recognition_results(upload_id);
CREATE INDEX idx_recognition_results_created_at ON recognition_results(created_at DESC);


CREATE VIEW recognition_summary AS
SELECT 
    u.id as upload_id,
    u.filename,
    u.file_type,
    u.file_size,
    u.upload_date,
    rr.recognized_text,
    rr.confidence_score,
    rr.processing_time,
    rr.created_at as recognition_date
FROM uploads u
LEFT JOIN recognition_results rr ON u.id = rr.upload_id;


\d uploads
\d recognition_results


\di


COMMENT ON TABLE uploads IS 'Stores information about uploaded PDF files';
COMMENT ON TABLE recognition_results IS 'Stores text recognition results from PDF files';
COMMENT ON VIEW recognition_summary IS 'Combined view of uploads and recognition results';
COMMENT ON COLUMN uploads.file_type IS 'File type - always pdf';
COMMENT ON COLUMN recognition_results.confidence_score IS 'Confidence score between 0 and 1';


SELECT 'Database tables created successfully for PDF-only recognition system!' as status;