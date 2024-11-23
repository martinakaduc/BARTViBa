import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
grand_dir = os.path.abspath(os.path.join(parent_dir, '..'))
# Add the directories to sys.path
sys.path.extend([script_dir, parent_dir, grand_dir])

from GraphTranslation.apis.routes.base_route import BaseRoute
from objects.data import Corpus, statusMessage
from pipeline.changeCorpus import ChangeCorpus
from apis.routes.VIBA_translation import VIBA_translate
from apis.routes.BAVI_translation import BAVI_translate

from GraphTranslation.common.languages import Languages


class changeCorpus(BaseRoute):
    def __init__(self, region):
        super(changeCorpus, self).__init__(prefix="/changeCorpus")
        self.pipeline = ChangeCorpus(region)
        self.region = region

    def change_corpus_func(self, data: Corpus):
        self.pipeline(data.region)
        if Languages.SRC == 'VI':
            VIBA_translate.changePipeline(region=data.region)
        else:
            BAVI_translate.changePipeline(region=data.region)
        return statusMessage(200,f"Corpus changed successfully to {data.region}","","", Languages.SRC == 'VI')
        
    def create_routes(self):
        router = self.router

        @router.post("/app")
        async def change_corpus(data: Corpus):
            return await self.wait(self.change_corpus_func, data)
