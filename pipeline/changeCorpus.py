import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
grand_dir = os.path.abspath(os.path.join(parent_dir, '..'))
# Add the directories to sys.path
sys.path.extend([script_dir, parent_dir, grand_dir])

import yaml
from GraphTranslation.services.base_service import BaseServiceSingleton
from pipeline.translation import Translator
from objects.singleton import Singleton

class ChangeCorpus(BaseServiceSingleton):
    def __init__(self, region):
        super(ChangeCorpus, self).__init__(region=region)
        self.region = region

    def changeCorpus(self, changeTo):
        if os.path.exists("data/cache/info.yaml"):
            with open("data/cache/info.yaml", "r", encoding="utf-8") as f:
                # take "region" key from info.yaml
                data = yaml.safe_load(f)
                region = data.get('region', None)
                if region == changeTo:
                    return
        
        for cls in dict(Singleton._instances).keys():
            del Singleton._instances[cls]
            cls = None
            
        self.region = changeTo

    def __call__(self, changeTo):
        res = self.changeCorpus(changeTo=changeTo)
        return res

if __name__ == "__main__":
    translator = Translator(region="BinhDinh")
    print(translator("Đồng tiền là vô giá"))
    changeDictCorpus = ChangeCorpus("Gia Lai")
    newTranslator = changeDictCorpus.changeCorpus("GiaLai")
    print(newTranslator("Đồng tiền là vô giá"))

