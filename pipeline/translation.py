import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
grand_dir = os.path.abspath(os.path.join(parent_dir, '..'))
# Add the directories to sys.path
sys.path.extend([script_dir, parent_dir, grand_dir])

import time
import json
from GraphTranslation.services.base_service import BaseServiceSingleton
from GraphTranslation.pipeline.translation import TranslationPipeline, Languages, TranslationGraph
from pipeline.model_translate import ModelTranslator
from GraphTranslation.common.ner_labels import *

class Translator(BaseServiceSingleton):
    def __init__(self, region):
        super(Translator, self).__init__(region)
        self.model_translator = ModelTranslator(region)
        self.graph_translator = TranslationPipeline(region)
        self.graph_translator.eval()
        self.region = region
        
        f_ba = open('word_disambiguation/neighbor_ba.json')
        self.neighbor_ba = json.load(f_ba)
        f_ba.close()
        
        f_vi = open('word_disambiguation/neighbor_vi.json')
        self.neighbor_vi = json.load(f_vi)
        f_vi.close()

    @staticmethod
    def post_process(text):
        words = text.split()
        output = []
        for w in words:
            if len(output) == 0 or output[-1] != w:
                output.append(w)
                
        output = " ".join(output)
        special_chars = [',', '.', ':', '?', '!']
        for char in special_chars:
            if char in output:
                output = output.replace(' '+char, char)
        output = output[0].capitalize() + output[1:]
        return output
    
    def printMenu(self, list_of_words: list, output: str):
        # list_of_words is a tuple of [(TV, <current>), <list_of_translations>]
        for items in list_of_words:
            print(items)
        print("Do you want to change the current translation of any of the following words?")
        
        for i, items in enumerate(list_of_words):
            print("Current translation:", output)
            current_word = items[0][1]
            print("Current word:", current_word)
            print("Candidates words:")
            for index, candidate in enumerate(list(items[1])):
                print(index, '-----', candidate)
            choice = int(input("Choose index: "))
            chosen_word = items[1][choice]
            print("Chosen word:", chosen_word)
            # update output
            output = output.replace(current_word, chosen_word, 1)
            # update list of words
            item_list = list(items[0])
            item_list[1] = chosen_word
            list_of_words[i] = (tuple(item_list), items[1])

        print("Current translation:", output)
        return output

    def __call__(self, text: str, model: str = "BART_CHUNK"):
        if model is None:
            model = "BART_CHUNK"
            
        if model in ["BART_CHUNK", "BART_CHUNK_NER_ONLY"]:
            s = time.time()
            sentence = self.graph_translator.nlp_core_service.annotate(text, language=Languages.SRC)
            # print("NLP CORE TIME", time.time() - s)
            # print("Mapped words", sentence.mapped_words)
            sentence = self.graph_translator.graph_service.add_info_node(sentence) # Update info about the NER
            # print(sentence.mapped_words)
            translation_graph = TranslationGraph(src_sent=sentence)
            
            control_mapped = translation_graph.update_src_sentence()         # Vị trí cần thực hiện việc translate các token trong dictionary
            
            if model == "BART_CHUNK":
                mapped_words = [w for w in translation_graph.src_sent if len(w.translations) > 0 or w.is_ner
                                or w.is_end_sent or w.is_end_paragraph or w.is_punctuation or w.is_conjunction]
            else:
                mapped_words = [w for w in translation_graph.src_sent if w.is_ner
                                or w.is_end_sent or w.is_end_paragraph or w.is_punctuation or w.is_conjunction]
            # print("Mapped words", sentence.mapped_words)
            # print(mapped_words)
            # print(control_mapped)

            result = []
            src_mapping = []
            i = 0
            while i < len(mapped_words):
                #print("Result now is", result)
                src_from_node = mapped_words[i]
                if src_from_node.is_ner:    # Apply các token là NER (Name entity or Number)
                    ner_text = self.graph_translator.translate_ner(src_from_node) # Translating the dictionary in HERE
                    if src_from_node.ner_label in [NUM]:
                        result.append(ner_text.lower())
                    else:
                        result.append(ner_text)
                else:   # Apply the token không phải NER
                    translations = []
                    ## Cái này là em chữa cháy tạm thời một số edge cases gặp trục trặc khi tích hợp word disambiguation của em
                    if src_from_node.text in ["@","/@","//@"]:
                        pass
                    elif src_from_node.text in [',', '.', ':', '?', '!']:
                        result.append(src_from_node.text)
                    else:
                        translations = src_from_node.translations
                        if len(translations) == 1:
                            result.append(translations[0].text)
                        else:
                            result.append(translations)


                src_mapping.append([src_from_node])
                if(i == len(mapped_words) - 1):
                    break
                src_to_node = mapped_words[i + 1]
                if src_from_node.end_index < src_to_node.begin_index - 1:
                    s = time.time()
                    chunk = translation_graph.src_sent.get_chunk(src_from_node.end_index,
                                                                 src_to_node.begin_index)
                    print("Detected chunk:", chunk)
                    if chunk is not None:
                        chunk_text = chunk.text
                        chunk_text = chunk_text.replace("//@", "").replace("/@", "").replace("@", "").replace(".", "").strip()
                        if len(chunk_text) > 0:
                            translated_chunk = self.model_translator.translate_cache(chunk_text) # Using BARTPho translation
                            result.append(translated_chunk)
                            print(f"CHUNK TRANSLATE {chunk.text} -> {translated_chunk} : {time.time() - s}")
                i += 1

            result_text = [res if type(res) == str else [r.text for r in res] for res in result]
            print("Result before scoring", result_text)

            if len(result) >= 3:
                for i in range(len(result)):
                    if not isinstance(result[i], str):
                        scores = [0] * len(result[i])
                        #### Choose by heuristic ####
                        dist = 4
                        coeff = [0.8,0.6,0.4,0.2]
                        #############################
                        before_word = []
                        next_word = []
                        idx = 0
                        while i - idx > 0 and idx < dist and isinstance(result[i - idx - 1], str):
                            before_word.append(result[i - idx - 1])
                            idx += 1
                        
                        idx = 0
                        while i + idx < len(result) - 1 and idx < dist and isinstance(result[i + idx + 1], str):
                            next_word.append(result[i + idx + 1])
                            idx += 1
                        # print(before_word,", ",next_word)
                        if next_word == [] and before_word == []:
                            result[i] = result[i][0].text
                            continue

                        candidates = result[i]
                        max_score = 0
                        best_candidate = None

                        if Languages.SRC == 'VI':
                            neighbor = self.neighbor_ba
                        else:
                            neighbor = self.neighbor_vi

                        for j in range(len(candidates)):
                            candidate_text = candidates[j].text
                            if candidate_text not in neighbor:
                                continue
                            neighbor_list = list(neighbor[candidate_text].keys())
                            for k in range(len(before_word)):
                                if before_word[k].isnumeric():
                                    before_word[k] = 'NUM'
                                if before_word[k] in neighbor_list:
                                    scores[j] += coeff[k]
                            for k in range(len(next_word)):
                                if next_word[k].isnumeric():
                                    next_word[k] = 'NUM'
                                if next_word[k] in neighbor_list:
                                    scores[j] += coeff[k]
                            if scores[j] > max_score:
                                max_score = scores[j]
                                best_candidate = candidates[j]

                        if (best_candidate is not None):
                            result[i] = best_candidate.text
                            print("CANDIDATES", [c.text for c in candidates], "\n>>> BEST CANDIDATE >>>", best_candidate.text)
                            print(f"Word '{best_candidate.text}': {round(max_score,2)}")
                        else:
                            if len(result[i]) == 0:
                                result[i] = ''
                            else:
                                result[i] = result[i][0].text

                    if i > 0 and (result[i-1].endswith("/@") or result[i-1].endswith("//@")):
                        result[i] = result[i].capitalize()
            else:
                result = [res if type(res) == str else res[0].text for res in result]

            output = result
            print("Output", output)
            output = "  ".join(output).replace("//@", "\n").replace("/@", ".").replace("@", "")
            while "  " in output or ". ." in output:
                output = output.replace("  ", " ").replace(". .", ".")
            return self.post_process(output.strip())

        else:
            output = self.model_translator.translate(text)
            output = output[0].capitalize() + output[1:]
            return self.post_process(output)


if __name__ == "__main__":
    translator = Translator("GiaLai")
    # print(translator("abŭt krĕnh adrang"))
    # print(translator("B`ai bơ tho tho ̆ ng Vĩnh Thạch. nan Vĩnh Thạch b`ai pơhrăm"))
    translator("một chuỗi hành động các hành động thiết thực")
    # print(translator("Cho một quả trầu cau. Hôm này trời đẹp"))
