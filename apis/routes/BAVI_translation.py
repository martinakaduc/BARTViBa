from GraphTranslation.apis.routes.base_route import BaseRoute
import yaml
# import Adder
import os
from pipeline.reverseTranslation import reverseTrans
from objects.data import statusMessage
from GraphTranslation.common.languages import Languages
from objects.data import Data
from GraphTranslation.config.config import Config
# Translator
from pipeline.translation import Translator

class BAVI_translate(BaseRoute):
    region: str
    pipeline: Translator

    def __init__(self, region):
        super(BAVI_translate, self).__init__(prefix="/translate")
        BAVI_translate.pipeline = Translator(region=region)
        BAVI_translate.region = region
        BAVI_translate.pipelineRev = reverseTrans(region=region)

    def translate_func(data: Data):
        if Languages.SRC == 'VI':
            BAVI_translate.pipeline = Translator(region=data.region)
            BAVI_translate.region = data.region
            BAVI_translate.pipelineRev = reverseTrans(region=data.region)
            BAVI_translate.pipelineRev()
            BAVI_translate.pipeline = Translator(BAVI_translate.region)
                
            if os.path.exists("data/cache/info.yaml"):
                os.remove("data/cache/info.yaml")
                with open("data/cache/info.yaml", "w") as f:
                    yaml.dump({"region": BAVI_translate.region}, f)
                    yaml.dump({"SRC": Languages.SRC}, f)
                    yaml.dump({"DST": Languages.DST}, f)
                    # count number of sentences in train, valid, test of the region
                    datapath = "data/" + BAVI_translate.region + '/'
                    # count number of sentences in train, valid, test of the region
                    with open(datapath + Config.src_monolingual_paths[0], "r", encoding='utf-8') as f1:
                        src_train_count = len(f1.readlines())
                    with open(datapath + Config.src_monolingual_paths[1], "r", encoding='utf-8') as f2:
                        src_valid_count = len(f2.readlines())
                    with open(datapath + Config.src_mono_test_paths[0], "r", encoding='utf-8') as f3:
                        src_test_count = len(f3.readlines())
                    with open(datapath + Config.dst_monolingual_paths[0], "r", encoding='utf-8') as f4:
                        dst_train_count = len(f4.readlines())
                    with open(datapath + Config.dst_monolingual_paths[1], "r", encoding='utf-8') as f5:
                        dst_valid_count = len(f5.readlines())
                    with open(datapath + Config.dst_mono_test_paths[0], "r", encoding='utf-8') as f6:
                        dst_test_count = len(f6.readlines())
                    with open("data/cache/info.yaml", "a") as f:
                        yaml.dump({
                            "src_train": src_train_count,
                            "src_valid": src_valid_count,
                            "src_test": src_test_count,
                            "dst_train": dst_train_count,
                            "dst_valid": dst_valid_count,
                            "dst_test": dst_test_count
                        }, f)
                print(open("data/cache/info.yaml", "r").read())
        #print("current region:", BAVI_translate.region)
        #print("addresss of pipeline:", BAVI_translate.pipeline)
        out_str = BAVI_translate.pipeline(data.text, model=data.model)
        #print("Translating data")
        return statusMessage(status=200, 
                             message="Translated successfully", 
                             src=data.text, 
                             tgt=out_str, 
                             fromVI=(Languages.SRC == 'VI'))
    
    @staticmethod
    def changePipelineRemoveGraph(region: str):
        determined_json_graph = 'data/cache/BAVI/{region}-graph.json'.format(region=region)
        if os.path.exists(determined_json_graph):
            os.remove(determined_json_graph)
        
        if os.path.exists("data/cache/info.yaml"):
            os.remove("data/cache/info.yaml")
            with open("data/cache/info.yaml", "w") as f:
                yaml.dump({"region": BAVI_translate.region}, f)
                yaml.dump({"SRC": Languages.SRC}, f)
                yaml.dump({"DST": Languages.DST}, f)

                # count number of sentences in train, valid, test of the region
                datapath = "data/" + BAVI_translate.region + '/'
                # count number of sentences in train, valid, test of the region
                with open(datapath + Config.src_monolingual_paths[0], "r", encoding='utf-8') as f1:
                    src_train_count = len(f1.readlines())
                with open(datapath + Config.src_monolingual_paths[1], "r", encoding='utf-8') as f2:
                    src_valid_count = len(f2.readlines())
                with open(datapath + Config.src_mono_test_paths[0], "r", encoding='utf-8') as f3:
                    src_test_count = len(f3.readlines())
                with open(datapath + Config.dst_monolingual_paths[0], "r", encoding='utf-8') as f4:
                    dst_train_count = len(f4.readlines())
                with open(datapath + Config.dst_monolingual_paths[1], "r", encoding='utf-8') as f5:
                    dst_valid_count = len(f5.readlines())
                with open(datapath + Config.dst_mono_test_paths[0], "r", encoding='utf-8') as f6:
                    dst_test_count = len(f6.readlines())

                with open("data/cache/info.yaml", "a") as f:
                    yaml.dump({
                        "src_train": src_train_count,
                        "src_valid": src_valid_count,
                        "src_test": src_test_count,
                        "dst_train": dst_train_count,
                        "dst_valid": dst_valid_count,
                        "dst_test": dst_test_count
                    }, f)

            print(open("data/cache/info.yaml", "r").read())
        
        BAVI_translate.region = region
        BAVI_translate.pipeline = Translator(region)
    
    
    def create_routes(self):
        router = self.router

        @router.post("/ba_vi")
        async def translate(data: Data):
            return await self.wait(BAVI_translate.translate_func, data)

