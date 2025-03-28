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
   
3. **Access the model**
   
   ```bash
   huggingface-cli login
   ```
   You will be promoted to enter the access token which you can find: https://huggingface.co/settings/tokens
   
   <img width="937" alt="diarization_accesstoken" src="https://github.com/user-attachments/assets/5e766cd7-45ef-4b2b-8d80-cc608d86e77c" />

4. **Running the Flask-ML Server**
   Start the Flask-ML server to work with RescueBox for predictions:

   ```bash
   python app.py
   ```   
   The server will start running on 127.0.0.1 5000

5. **Download and run RescueBox Desktop from the following link: [Rescue Box Desktop](https://github.com/UMass-Rescue/RescueBox-Desktop/releases)**

   Open the RescueBox Desktop application and register the model
   
   <img width="495" alt="diarization_register" src="https://github.com/user-attachments/assets/b223ff7b-e941-44d1-a6e8-7c95a46487a3" />

   Run the model
   
   Set the Input and Output directory.
   
   <img width="749" alt="diarization_directory" src="https://github.com/user-attachments/assets/5cbb8304-59de-49b7-9fc6-78eb7a5e7e16" />


   Input directory should have an audio file and an output directory where the json file with the predictions will be outputted.
   
   Results will be displayed
  
   <img width="735" alt="diarization_result" src="https://github.com/user-attachments/assets/566446ca-49e6-41e6-9889-96140476bb6f" />

