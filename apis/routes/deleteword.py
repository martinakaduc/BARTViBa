# get add_word_to_dict function from add_word.py
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
grand_dir = os.path.abspath(os.path.join(parent_dir, '..'))
# Add the directories to sys.path
sys.path.extend([script_dir, parent_dir, grand_dir])

from GraphTranslation.apis.routes.base_route import BaseRoute
from objects.data import textInput
import yaml
# import Adder
from pipeline.deleteword import DeleteWord
from apis.routes.VIBA_translation import VIBA_translate
from apis.routes.VIBA_translation import VIBA_translate
from GraphTranslation.common.languages import Languages
from objects.data import statusMessage


class deleteWord(BaseRoute):
    def __init__(self, region):
        super(deleteWord, self).__init__(prefix="/deleteword")
        self.region = region
        self.pipeline = DeleteWord(self.region)

    def delete_func(self, data: textInput):
        with open('data/cache/info.yaml', 'r+') as f:
            # if the "region" field is not KonTum then delete
            dt = yaml.safe_load(f)
            region = dt.get('region', None)
            self.region = region
        success = self.pipeline(data.text, data.fromVI)
        if success:
            if Languages.SRC == 'VI':
                VIBA_translate.changePipelineRemoveGraph(region=self.region)
            else:
                VIBA_translate.changePipelineRemoveGraph(region=self.region)
            return statusMessage(200,"Words deleted successfully","", Languages.SRC == 'VI')
        else:
            return statusMessage(400,"Words not found","",Languages.SRC == 'VI')
    
    def create_routes(self):
        router = self.router

        @router.post("/app")
        async def delete_word(data: textInput):
            return await self.wait(self.delete_func, data)