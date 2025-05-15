# 🔊 Audio-Diarization

  

Speaker Diarization is a system that identifies and separates speakers in an audio file, with their respective timestamps and speaker labels. This model is integrated with a Automatic Speech Recognition (ASR) model to transcribe each speaker's audio. This model efficiently inputs a folder with audio files and presents a csv file containing speaker separation with their corresponding time stamps and audio transcription.

  

This process aids child rescue efforts by distinguishing victim and abuser voices, providing crucial evidence for court proceedings and in distinguishing speakers from background noise during criminal investigations

  

## Installation

  

  

1.  **Clone the Repository**:


	```bash
	git  clone  https://github.com/UMass-Rescue/Audio-Diarization.git

	cd  Audio-Diarization
	```

  

  

2.  **Install Dependencies:**

	For the best results create a virtaul environment. You can use any method to create a virtual environment!

	One of the ways to create a virtual environment is listed below

	```bash
	python -m venv <virtual_env_name>
	```
	Activate the virtual environment

	#### For MacOS/Linux run

	```bash
	source <virtual_env_name>/bin/activate
	```

	#### For Windows run

	```bash
	cd <virtual_env_name>\Scripts
	.\activate
	```

	Install the required Python packages using the following command:

	```bash
	pip  install  -r  requirements.txt
	```
	Make sure to install ffmpeg on your system if you don't already have it

	#### For MacOS

	If you already have homebrew you can use the command listed below to directly install ffmpeg. If not you can follow the [documentation](https://docs.brew.sh/Installation) to install homebrew and then use the command listed below.

	```bash
	brew  install  ffmpeg
	```

	#### For Windows

	Use this [link to install the ffmpeg executable](https://www.ffmpeg.org/download.html#build-windows). Click on the windows icon and use the windows build from gyan.dev

	Follow the installation instructions mentioned in the installer
	Add ffmpeg to the environment variables to make to accessible globally

  
  

3.  **Access the model **

	This step is not longer needed! Unless you want to run the model API directly. By default this application is set to run the local model pipeline for pyannote/speaker-diarization-3.0

	```bash
	huggingface-cli  login
	```

	You will be prompted to enter the access token which you can find: https://huggingface.co/settings/tokens

	<img  width="937"  alt="diarization_accesstoken"  src="https://github.com/user-attachments/assets/5e766cd7-45ef-4b2b-8d80-cc608d86e77c"  />
	  
	  

4.  **Running the Flask-ML Server**

	Start the Flask-ML server to work with RescueBox for Audio Diarization:

	```bash
	python  model_3endpoints.py
	```
	The server will start running on 127.0.0.1 5000


5.  **Download and run RescueBox Desktop from the following link: [Rescue Box Desktop](https://github.com/UMass-Rescue/RescueBox-Desktop/releases)**

	Open the RescueBox Desktop application and register the model
	<img  width="495"  alt="diarization_register"  src="https://github.com/user-attachments/assets/b223ff7b-e941-44d1-a6e8-7c95a46487a3"  />
	Run the model

	  

	Set the Input and Output directory.

	<img  width="749"  alt="diarization_directory"  src="https://github.com/user-attachments/assets/5cbb8304-59de-49b7-9fc6-78eb7a5e7e16"  />

	Input directory should have an audio file and an output directory where the csv file with the speaker seperation, time stamps and audio transcription is found

	Results will be displayed as follows






