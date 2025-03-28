# Audio-Diarization

Speaker Diarization – Identifying and separating speakers in an audio file, transcribing the speech with timestamps and speaker labels. 

This process aids child rescue efforts by distinguishing victim and abuser voices, providing crucial evidence for court proceedings.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/UMass-Rescue/Audio-Diarization.git 
   cd Audio-Diarization
   ```

2. **Install Dependencies:**
   Install the required Python packages using the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Flask-ML Server**
   Start the Flask-ML server to work with RescueBox for predictions:

   ```bash
   python app.py
   ```

   The server will start running on 127.0.0.1 5000

   **Download and run RescueBox Desktop from the following link: [Rescue Box Desktop](https://github.com/UMass-Rescue/RescueBox-Desktop/releases)**

   Open the RescueBox Desktop application and register the model

   Run the model

   Set the Input and Output directory.

   Input directory should have an audio file and an output directory where the json file with the predictions will be outputted.
  
