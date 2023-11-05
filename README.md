1) Create a service account to authenticate your API requests:

`gcloud iam service-accounts create speech-to-text-quickstart --project 
accessgdrivestreamlit`

2) Grant your service account the roles/viewer Role:
`gcloud projects add-iam-policy-binding accessgdrivestreamlit \
   --member serviceAccount:speech-to-text-quickstart@accessgdrivestreamlit.iam.gserviceaccount.com \
--role roles/viewer`

3) Create a service account key:
`gcloud iam service-accounts keys create speech-to-text-key.json 
--iam-account speech-to-text-quickstart@accessgdrivestreamlit.iam.gserviceaccount.com`

4) Set the key as your default credentials:
`export GOOGLE_APPLICATION_CREDENTIALS=speech-to-text-key.json`
  

5) Install `brew install portaudio`

6) Install `brew install ffmpeg`


### activate the text to speech

1) Create a service account to authenticate your API requests:

`gcloud iam service-accounts create text-to-speech-quickstart --project accessgdrivestreamlit`

2) Grant your service account the Text-to-Speech API User role:
`gcloud projects add-iam-policy-binding accessgdrivestreamlit --member serviceAccount:text-to-speech-quickstart@accessgdrivestreamlit.iam.gserviceaccount.com --role roles/viewer
`

3) Create a service account key:

`gcloud iam service-accounts keys create text-to-speech-key.json --iam-account text-to-speech-quickstart@accessgdrivestreamlit.iam.gserviceaccount.com`

4) Set the key as your default credentials:

`export GOOGLE_APPLICATION_CREDENTIALS=text-to-speech-key.json`
