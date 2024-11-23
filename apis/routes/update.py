from GraphTranslation.apis.routes.base_route import BaseRoute
from objects.data import ModifyData
import yaml
# import Adder
from pipeline.updateword import Update
from apis.routes.VIBA_translation import VIBA_translate
from apis.routes.BAVI_translation import BAVI_translate
from objects.data import statusMessage
from GraphTranslation.common.languages import Languages


class updateWord(BaseRoute):
    def __init__(self, region):
        super(updateWord, self).__init__(prefix="/updateword")
        self.region = region
        self.pipeline = Update(self.region)

    def update_word(self, data: ModifyData):
        with open('data/cache/info.yaml', 'r+') as f:
            # if the "region" field is not KonTum then delete
            dt = yaml.safe_load(f)
            region = dt.get('region', None)
            self.region = region
        success = self.pipeline(data.word, data.translation, data.fromVI)
        if success:
            if Languages.SRC == 'VI':
                VIBA_translate.changePipelineRemoveGraph(region=self.region)
            else:
                BAVI_translate.changePipelineRemoveGraph(region=self.region)
            return statusMessage(200,"Word updated successfully","", Languages.SRC == 'VI')
        else:
            return statusMessage(400,"Word not found","",Languages.SRC == 'VI')
    
    def create_routes(self):
        router = self.router

        @router.post("/app")
        async def add_word(data: ModifyData):
            return await self.wait(self.update_word, data)