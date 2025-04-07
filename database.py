import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class DiarizationDatabase:
    def __init__(self, db_path: str = "diarization.db"):
        self.db_path = Path(db_path)
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create audio files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audio_files (
                    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    duration REAL,
                    num_speakers INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create speaker segments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS speaker_segments (
                    segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    speaker_label TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    duration REAL GENERATED ALWAYS AS (end_time - start_time) STORED,
                    FOREIGN KEY (file_id) REFERENCES audio_files (file_id)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_speaker 
                ON speaker_segments (file_id, speaker_label)
            """)
            
            conn.commit()

    def save_audio_file(self, filename: str, file_path: str, duration: Optional[float] = None) -> int:
        """Save audio file metadata and return file_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO audio_files 
                (filename, file_path, duration) 
                VALUES (?, ?, ?)
                ON CONFLICT(filename) DO UPDATE SET
                file_path=excluded.file_path,
                duration=excluded.duration
                RETURNING file_id""",
                (filename, str(file_path), duration)
            )
            file_id = cursor.fetchone()[0]
            conn.commit()
            return file_id

    def save_speaker_segments(self, file_id: int, segments: List[Dict[str, float]]) -> None:
        """Save speaker segments for a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete existing segments if any
            cursor.execute(
                "DELETE FROM speaker_segments WHERE file_id = ?",
                (file_id,)
            )
            
            # Insert new segments
            cursor.executemany(
                """INSERT INTO speaker_segments 
                (file_id, speaker_label, start_time, end_time)
                VALUES (?, ?, ?, ?)""",
                [(file_id, seg["speaker"], seg["start"], seg["end"]) for seg in segments]
            )
            
            # Update speaker count
            cursor.execute(
                """UPDATE audio_files 
                SET num_speakers = (
                    SELECT COUNT(DISTINCT speaker_label) 
                    FROM speaker_segments 
                    WHERE file_id = ?
                )
                WHERE file_id = ?""",
                (file_id, file_id)
            )
            
            conn.commit()

    def get_file_results(self, filename: str) -> Dict:
        """Get all diarization results for a file"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get file metadata
            cursor.execute(
                """SELECT * FROM audio_files 
                WHERE filename = ?""",
                (filename,)
            )
            file_data = cursor.fetchone()
            
            if not file_data:
                return None
                
            # Get segments
            cursor.execute(
                """SELECT speaker_label, start_time, end_time 
                FROM speaker_segments 
                WHERE file_id = ?
                ORDER BY start_time""",
                (file_data["file_id"],)
            )
            segments = cursor.fetchall()
            
            return {
                "metadata": dict(file_data),
                "segments": [dict(seg) for seg in segments]
            }

    def get_all_files(self) -> List[Dict]:
        """Get list of all processed files"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audio_files ORDER BY processed_at DESC")
            return [dict(row) for row in cursor.fetchall()]