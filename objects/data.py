from pydantic import BaseModel
from typing import Optional, List

class Data(BaseModel):
    region: str
    text: str
    model: Optional[str]

    def __init__(self, text: str, region: str = "BinhDinh",  model: str = None):
        super(Data, self).__init__(region=region, text=text, model=model)
        self.region = region
        self.text = text
        self.model = model

class AddData(BaseModel):
    # word and translation are both array type
    word: str
    translation: str
    fromVI: bool

    def __init__(self, word, translation, src):
        super(AddData, self).__init__(word=word, translation=translation, src=src)
        self.word = word
        self.translation = translation
        self.src = src

class ModifyData(BaseModel):
    word: str
    translation: str
    fromVI: bool

    def __init__(self, word, translation):
        super(ModifyData, self).__init__(word=word, translation=translation)
        self.word = word
        self.translation = translation

class Corpus(BaseModel):
    region: str

    def __init__(self, region: str):
        super(Corpus, self).__init__(region=region)
        self.region = region

class textInput(BaseModel):
    text: str
    fromVI: bool

    def __init__(self, text: str):
        super(textInput, self).__init__(text=text)
        self.text = text
        
class DataSpeechDelete(BaseModel):
    urls: List[str]

    def __init__(self, urls: List[str]):
        super(DataSpeechDelete, self).__init__(urls=urls)
        self.urls = urls
        
class DataSpeech(BaseModel):
    text: str
    gender: Optional[str]
    region: Optional[str]

    def __init__(self, text: str, gender: str = None, region: str = None):
        super(DataSpeech, self).__init__(text=text, gender=gender, region=region)
        self.text = text
        self.gender = gender
        self.region = region
        
        
class OutDataSpeech(BaseModel):
    speech: str
    speech_fm: Optional[str]

    def __init__(self, speech: str, speech_fm: str = None):
        super(OutDataSpeech, self).__init__(speech=speech, speech_fm=speech_fm)
        self.speech = speech
        self.speech_fm = speech_fm


class statusMessage(BaseModel):
    status: int
    message: str
    src: str
    tgt: str
    fromVI: bool

    def __init__(self, status: int, message: str, src: str, tgt: str, fromVI: bool):
        super(statusMessage, self).__init__(status=status, message=message, src=src, tgt=tgt, fromVI=fromVI)
        self.status = status
        self.message = message
        self.src = src
        self.tgt = tgt
        self.fromVI = fromVI
