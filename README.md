# Audio-Diarization

Hello~ 
To run the diarization model follow the steps below

## Create a Virtual Environment

Please use any method to create a virtual environment. I have used venv and have listed the steps for that.
```
python -m venv <virtual_env_name>
```
Once you have created a virtual environment enter it to make sure there is no clash in dependencies. Once again one of the commands to activate the virtual environment is listed below

```
source <virtual_env_name>/bin/activate
```
##  Install the Requirements

To make sure we have all the libraries needed to execute these models you will need to run the requirements.txt file. Follow the command listed below

```
pip install -r requirements.txt
```

## Get hugging face token

Log into [Hugging Face](https://huggingface.co/) and get the auth token.
Go to pyan.py repalace 'HUGGING_FACE_TOKEN' on line 5 with the tokem obtained

## Run the model

Once all these steps are complete we can run the test audio file simply by

```
python pyan.py
```

