from GraphTranslation.apis.routes.base_route import BaseRoute

from objects.data import Data, statusMessage
from pipeline.translation import Translator
import os
import yaml
from GraphTranslation.common.languages import Languages
from GraphTranslation.config.config import Config
from pipeline.reverseTranslation import reverseTrans
from fastapi.responses import JSONResponse
import re

class VIBA_translate(BaseRoute):
    region: str
    pipeline: Translator

    def __init__(self, region):
        super(VIBA_translate, self).__init__(prefix="/translate")
        # VIBA_translate.pipeline = Translator(region=region)
        VIBA_translate.region = region
        VIBA_translate.pipelines = {}
        # Tạo các pipeline sẵn cho mỗi corpus
        VIBA_translate.pipelines["BinhDinh"] = Translator(region="BinhDinh")
        VIBA_translate.pipelines["KonTum"] = Translator(region="KonTum")
        VIBA_translate.pipelines["GiaLai"] = Translator(region="GiaLai")
        VIBA_translate.pipelineRev = reverseTrans(region=region)

    def translate_func(data: Data):
        
        # Kiểm tra region và chọn pipeline phù hợp
        region = data.region

        # Nếu region không tồn tại trong danh sách pipeline, trả lỗi
        if region not in VIBA_translate.pipelines:
            return statusMessage(status=400, message="Unsupported region")

        # Chọn pipeline theo region
        VIBA_translate.pipeline = VIBA_translate.pipelines[region]
        #em mới làm phần VI_BA thôi, còn BA_VI thì chưa chỉnh ạ 
        if Languages.SRC == 'BA':
            VIBA_translate.pipeline = Translator(region=data.region)
            VIBA_translate.region = data.region
            VIBA_translate.pipelineRev = reverseTrans(region=data.region)
            VIBA_translate.pipelineRev()
            VIBA_translate.pipeline = Translator(VIBA_translate.region)
            if os.path.exists("data/cache/info.yaml"):
                os.remove("data/cache/info.yaml")
                with open("data/cache/info.yaml", "w") as f:
                    yaml.dump({"region": VIBA_translate.region}, f)
                    yaml.dump({"SRC": Languages.SRC}, f)
                    yaml.dump({"DST": Languages.DST}, f)
                    # count number of sentences in train, valid, test of the region
                    datapath = "data/" + VIBA_translate.region + '/'
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
        #print("current region:", VIBA_translate.region)
        #print("addresss of pipeline:", VIBA_translate.pipeline)
        out_str = VIBA_translate.pipeline(data.text, model=data.model)
        #print("Translating data")
       
        print(out_str)
        return statusMessage(status=200, 
                             message="Translated successfully", 
                             src=data.text, 
                             tgt=out_str, 
                             fromVI=(Languages.SRC == 'VI'))
    
    @staticmethod
    def changePipelineRemoveGraph(region: str):
        determined_json_graph = 'data/cache/VIBA/{region}-graph.json'.format(region=region)
        if os.path.exists(determined_json_graph):
            os.remove(determined_json_graph)
        
        if os.path.exists("data/cache/info.yaml"):
            os.remove("data/cache/info.yaml")
            with open("data/cache/info.yaml", "w") as f:
                yaml.dump({"region": VIBA_translate.region}, f)
                yaml.dump({"SRC": Languages.SRC}, f)
                yaml.dump({"DST": Languages.DST}, f)

                # count number of sentences in train, valid, test of the region
                datapath = "data/" + VIBA_translate.region + '/'
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
        
        VIBA_translate.region = region
        VIBA_translate.pipeline = Translator(region)

    @staticmethod
    def changePipeline(region: str):
        if os.path.exists("data/cache/info.yaml"):
            os.remove("data/cache/info.yaml")
            with open("data/cache/info.yaml", "w") as f:
                yaml.dump({"region": VIBA_translate.region}, f)
                yaml.dump({"SRC": Languages.SRC}, f)
                yaml.dump({"DST": Languages.DST}, f)

                # count number of sentences in train, valid, test of the region
                datapath = "data/" + VIBA_translate.region + '/'
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

        VIBA_translate.region = region
        VIBA_translate.pipeline = Translator(region)

    def create_routes(self):
        router = self.router

        @router.post("/vi_ba")
        async def translate(data: Data):
            return await self.wait(VIBA_translate.translate_func, data)
