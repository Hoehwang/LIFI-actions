# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import pandas as pd
import re, random
from bs4 import BeautifulSoup as bs
import requests

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

syn = pd.read_csv("./actions/SYN.csv")
res = pd.read_csv("./actions/RESPONSE_EXP_FIN.csv")

class ActionRephraseResponse(Action):

    def name(self) -> Text:
        return "action_rephrase_fintech"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # print(tracker.latest_message["text"])
        entis = [a.get("entity") for a in tracker.latest_message["entities"]]
        ent_name = [a.get("value") for a in tracker.latest_message["entities"]]
        print(ent_name)
        inti = tracker.get_intent_of_latest_message()

        if len(entis) > 0:
            if inti == 'QUERY_DICTIONARY':
                try:
                    ind = [a for a, b in enumerate(syn["entity"].tolist()) if ent_name[0] in b][0]
                except IndexError:
                    ind = [a for a, b in enumerate(syn["entity"].tolist()) if ent_name[0][:-1] in b][0]
            else:
                ind = [a for a, b in enumerate(syn["intent"].tolist()) if b == entis[0]][0]
            enti = syn["norm"].tolist()[ind]
            print(enti)
            ind = [a for a, b in enumerate(res["intent"].tolist()) if str(b) == str(inti)][0]
            fres = str(res["response"].tolist()[ind])
            if len(fres.split(' / ')) == 1:
                fin = str(enti).strip() + fres
            else:
                fres = random.sample(fres.split(' / '), 1)[0]
                fin = str(enti).strip() + fres

            dispatcher.utter_message(text=re.sub('[ ]{2,}', ' ', fin))
            dispatcher.utter_message(image="http://linito.kr/wp-content/uploads/2020/09/gold-20482960-e1627262297694.jpg")
            if inti == 'QUERY_DICTIONARY':
                utter_link_text = '%s%s' % (enti.strip(), res["utter_link"].tolist()[ind])

                if len(utter_link_text.split(' / ')) > 1:
                    utter_link_text = random.sample(utter_link_text.split(' / '), 1)[0]

                dispatcher.utter_message(text=utter_link_text)

                utter_send_link_text = res["utter_send_link"].tolist()[ind]
                if len(utter_send_link_text.split(' / ')) > 1:
                    utter_send_link_text = random.sample(utter_link_text.split(' / '), 1)[0]

                url = 'https://www.mk.co.kr/dic/desc.php?keyword=%s' % re.sub(' ', '', enti)
                req = requests.get(url)
                soup = bs(req.text, 'html.parser')
                crawled = soup.find('p', {'id': 'area_content'}).text.split('.')
                if len(crawled) > 2:
                    text_1 = '%s.' % '.'.join(crawled[:3])
                elif len(crawled) == 2:
                    text_1 = '%s.' % '.'.join(crawled[:2])
                else:
                    text_1 = '%s.' % '.'.join(crawled[:1])
                text_2 = '더 자세한 정보는 아래 링크를 통해 확인해주세요!\n%s [%s](%s)' % (utter_send_link_text, url, url)
                dispatcher.utter_message(text=text_1)
                dispatcher.utter_message(text=text_2)
            else:
                utter_link_text = '%s' % res["utter_link"].tolist()[ind]
                if len(utter_link_text.split(' / ')) > 1:
                    utter_link_text = random.sample(utter_link_text.split(' / '), 1)[0]
                utter_send_link_text = res["utter_send_link"].tolist()[ind]
                if len(utter_send_link_text.split(' / ')) > 1:
                    utter_send_link_text = random.sample(utter_send_link_text.split(' / '), 1)[0]

                dispatcher.utter_message(text=utter_link_text)
                dispatcher.utter_message(text=utter_send_link_text)

            utter_ask_more = res["utter_ask_more"].tolist()[ind]
            if len(utter_ask_more.split(' / ')) > 1:
                utter_ask_more = random.sample(utter_ask_more.split(' / '), 1)[0]
            dispatcher.utter_message(text=utter_ask_more)

        else:
            ind = [a for a, b in enumerate(res["intent"].tolist()) if str(b) == str(inti)][0]
            featureless = res["featureless"].tolist()[ind]
            if len(featureless.split(' / ')) > 1:
                featureless = random.sample(featureless.split(' / '), 1)[0]

            fin = str(featureless)
            dispatcher.utter_message(text=fin)

        return []
