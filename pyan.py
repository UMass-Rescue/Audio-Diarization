# instantiate the pipeline
from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.0",
  use_auth_token="HUGGING_FACE_TOKEN")

# run the pipeline on an audio file
diarization = pipeline("conv.wav")

# dump the diarization output to disk using RTTM format
with open("audio.rttm", "w") as rttm:
  diarization.write_rttm(rttm)
