import sqlite3
import whisper
import librosa

# Step 1: Set up SQLite Database
conn = sqlite3.connect('transcriptions.db')
cursor = conn.cursor()

# Create the table (if it doesn't exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    transcription TEXT
)
''')
conn.commit()

#Load Whisper Model for Transcription
transcription_model = whisper.load_model("base")  # Use "base", "small", "medium", or "large"

#Transcribe Audio Segments with Whisper
def transcribe_segment(audio_file, start_time, end_time):
    # Use Whisper to transcribe the entire audio file
    result = transcription_model.transcribe(audio_file, fp16=False, language="en", verbose=False)
    segments = result['segments']

    #Print all segments returned by Whisper
    print(f"All segments for {audio_file}:")
    for s in segments:
        print(f"Start: {s['start']}, End: {s['end']}, Text: {s['text']}")

    # Filter segments that fall within the specified time range
    relevant_segments = [s for s in segments if s['start'] >= start_time and s['end'] <= end_time]

    # Debugging
    print(f"Relevant segments for {start_time}-{end_time}:")
    for s in relevant_segments:
        print(f"Start: {s['start']}, End: {s['end']}, Text: {s['text']}")

    return " ".join([s['text'] for s in relevant_segments])

#Save Transcription to SQLite Database
def save_transcription(track_id, start_time, end_time, transcription):
    """
    Save the transcription to the SQLite database.
    """
    cursor.execute('''
    INSERT INTO transcriptions (track_id, start_time, end_time, transcription)
    VALUES (?, ?, ?, ?)
    ''', (track_id, start_time, end_time, transcription))
    conn.commit()

#Process Audio File
def process_audio(audio_file, track_id, segment_length=30):  # Increased segment length to 30 seconds
    """
    Process the audio file: split into segments and transcribe each segment.
    """
    #Get the total duration of the audio file
    duration = librosa.get_duration(path=audio_file)

    #Process each segment
    for start_time in range(0, int(duration), segment_length):
        end_time = min(start_time + segment_length, duration)

        #Transcribe the segment
        transcription = transcribe_segment(audio_file, start_time, end_time)

        #Save the result to the database
        save_transcription(track_id, start_time, end_time, transcription)

#Retrieve Transcriptions from the Database
def get_transcriptions():
    """
    Retrieve and display all transcriptions from the database.
    """
    cursor.execute('SELECT * FROM transcriptions')
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Track ID: {row[1]}, Start: {row[2]}, End: {row[3]}, Transcription: {row[4]}")


if __name__ == "__main__":
    # Example audio file and track ID
    audio_file = "tiny_tim.wav"  # Replace with your audio file path
    track_id = 1  # Replace with your track ID, modificastions required

    # Process the audio file
    process_audio(audio_file, track_id)

    # Retrieve and display the results
    get_transcriptions()

    # Close the database connection when done
    conn.close()