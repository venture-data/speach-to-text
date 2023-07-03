from moviepy.editor import VideoFileClip
import requests
import streamlit as st
from moviepy.editor import *
from pydub import AudioSegment
import math

class SplitWavAudioMubin():
    def __init__(self, filepath):
        # self.folder = folder
        self.filename = filepath.split('/')[-1]
        self.filepath = filepath
        
        self.audio = AudioSegment.from_wav(self.filepath)
    
    def get_duration(self):
        return self.audio.duration_seconds
    
    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(split_filename, format="wav")
        
    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) + ' Done')
            # if i == total_mins - min_per_split:
                # print('All splited successfully')

st.title("Video to Text")
st.write()

subscription_key = st.secrets["SUBSCRIPTION_KEY"]

url = "https://centralindia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"

headers = {
    'Content-type': 'audio/wav;codec="audio/pcm";',
    'Ocp-Apim-Subscription-Key': st.secrets["SUBSCRIPTION_KEY"]
    
}

st.write("uploading file")
uploaded_file = st.file_uploader("Choose a video...")


if uploaded_file is not None:
    print("type(uploaded_file) --> ", type(uploaded_file))
    with open("sample.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
        video = VideoFileClip("sample.mp4")
        video.audio.write_audiofile("sample.mp3")
        sound = AudioSegment.from_mp3("sample.mp3")
        sound.export("sample.wav", format="wav")

        split_wav = SplitWavAudioMubin("sample.wav")
        split_wav.multiple_split(min_per_split=1)
        files = os.listdir('./')
        split_files = []
        for file in files:
          if file.endswith('_sample.wav'):
            split_files.append(file)
        split_files = sorted(split_files)
    st.write("Processing video")
    batch_size = len(split_files)
    st.write("Batch size for video processing is ", batch_size)
    count = 1
    for wav in split_files:
      st.write('processing batch --> ', count)
      with open(wav, 'rb') as payload:
          response = requests.request("POST", url, headers=headers, data=payload)
          try:
              long_text = response.text.split('DisplayText":')[1].split(',"Offset')[0]
              st.write(long_text)
          except:
              st.write('Batch seems to be empty')
      count = count+1
          # print(response.text)
