import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
import json
import torch
from flask import Flask,request,Response
import dl_translate as dlt
import traceback
from typing import List,Dict
from itertools import groupby
from operator import itemgetter
import warnings
import requests
warnings.filterwarnings('ignore')
from ltp import LTP
import nltk
import re

ltp = LTP(pretrained_model_name_or_path='LTP/small')

mt_m2m100 = dlt.TranslationModel(model_or_path='facebook/m2m100_418M',model_family='m2m100',device='cuda')
"""2021/05/20新增mbart50模型"""
mt_mbart50 = dlt.TranslationModel(model_or_path='facebook/mbart-large-50-many-to-many-mmt',model_family='mbart50',device='cuda')
lang_code_map_m2m100 = dlt.utils.get_lang_code_map('m2m100')
lang_code_map_mbart50 = dlt.utils.get_lang_code_map('mbart50')
MAX_LENGTH = 200

def gen_batch_data(data=None, batch_size=32):
    """
    生成batch list数据
    :param data:
    :param batch_size:
    :return:
    """
    l = len(data)
    for ndx in range(0, l, batch_size):
        yield data[ndx:min(ndx + batch_size, l)]


def get_batch_data(data=None, batch_size=None, shuffle=False):
    """
    产生批数据
    :param data: 输入数据 列表
    :param batch_size: 批数据大小
    :param shuffle: 是否打乱数据
    :return:
    """
    rows = len(data)  # 数据条数
    indices = list(range(rows))
    # 是否打乱
    if shuffle:
        random.seed(2020)
        random.shuffle(indices)
    while True:
        batch_indices = np.asarray(indices[0:batch_size])
        indices = indices[batch_size:] + indices[:batch_size]

        print(indices)

        data = np.asarray(data)
        temp_data = data[batch_indices]
        yield temp_data.tolist()


def sent_tokenize(article:str,lang:str=None):

    if lang==None or lang=='Chinese' or lang=='Japanese':
        return ltp.sent_split([article])
    else:
        return nltk.sent_tokenize(article)


def process_format(doc:str):
    # doc = doc.replace('\n','<br>')
    emoji_pattern = re.compile(u'[\U00010000-\U0010ffff]')
    doc = emoji_pattern.sub('', doc)
    drop_http = re.compile(r'([http|https]*://[a-zA-Z0-9.?/&=:_]*|\n+|{[A-Z]+:\d+}|#|@+[a-zA-z_\d+]+)', re.S)
    # url_pattern = "(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|\n"
    doc = re.split(pattern=drop_http,string=doc)
    sent_list = list(filter(None,doc))
    sent_mask = []
    if len(sent_list)>0:
        sent_mask = [0 if re.match(drop_http,item) else 1 for item in sent_list ]
    return sent_list,sent_mask


def translate(article, source_lang, target_lang):
    try:
        sentence_ids = []
        split_sentence_list = []

        if not isinstance(article,str) or not isinstance(source_lang,str) or not isinstance(target_lang,str):
            raise TypeError()

        # if source_lang=='Cantonese' or source_lang =='TraditionalChinese':
        #     if target_lang != 'Chinese':
        #         raise ParamterException()
        #     return convert_traditional_2_simple_chinese(article)
        doc_split,doc_mask  = process_format(article)
        """
            doc_split:['In China’s tightly controlled internet space, the uncensored explosion of any topic must be seen as having the Communist Party’s acquiescence — if not outright backing. And so, the outpouring of online attacks directed at Western fashion brands caught up in the row over Xinjiang cotton has all the hallmarks of being official policy.', '\n\n', 'Read: ', 'https://bit.ly/3rwC8ou', '\n\n', '_______', '\n', '📱Download the app:', '\n', 'http://onelink.to/appledailyapp', '\n', '📰 Latest news:', '\n', 'http://appledaily.com/engnews/', '\n', '🐤 Follow us on Twitter:', '\n', 'https://twitter.com/appledaily_hk', '\n', '💪🏻 Subscribe and show your support:', '\n', 'https://bit.ly/2ZYKpHP', '\n\n', '#AppleDailyENG', '\n']
            doc_mask:[1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        """
        for index,item_split_text in enumerate(doc_split):
            if doc_mask[index]==0:
                pass
            else:
                if len(item_split_text)>MAX_LENGTH:
                    split_sentence = sent_tokenize(item_split_text,lang=source_lang)
                    '''单条数据太长导致翻译速度缓慢'''
                    # sentence_ids.extend([(index,i) for i in range(len(split_sentence))])
                    # split_sentence_list.extend(split_sentence)
                    tmp_sent = ''
                    tmp_ids = 0
                    for sent_index,sent in enumerate(split_sentence):
                        # 当前句子大于最大长度且他的前面有临时句子
                        if len(sent)>MAX_LENGTH and tmp_sent!='':
                            sentence_ids.append((index,tmp_ids))
                            split_sentence_list.append(tmp_sent)
                            tmp_sent = ''
                            tmp_ids += 1
                            sentence_ids.append((index,tmp_ids))
                            split_sentence_list.append(sent)
                            tmp_ids += 1
                        # 当前句子大于最大长度且他的前面无临时句子
                        elif len(sent)>MAX_LENGTH and tmp_sent=='':
                            sentence_ids.append((index,tmp_ids))
                            split_sentence_list.append(sent)
                            tmp_ids += 1
                        # 当前句子加临时句子长度小于最大长度
                        elif len(tmp_sent)+len(sent)<MAX_LENGTH:
                            tmp_sent += sent
                        # 当前句子加临时句子长度大于最大长度
                        else:
                            sentence_ids.append((index,tmp_ids))
                            split_sentence_list.append(tmp_sent)
                            tmp_sent = sent
                            tmp_ids+=1
                    if tmp_sent !='':
                        sentence_ids.append((index, tmp_ids))
                        split_sentence_list.append(tmp_sent)
                else:
                    sentence_ids.append((index,0))
                    split_sentence_list.append(item_split_text)
        assert source_lang in lang_code_map_m2m100 and target_lang in lang_code_map_m2m100
        result = []
        for batch_sentence in gen_batch_data(data=split_sentence_list,batch_size=32):
            if source_lang=='English':
                res = mt_mbart50.translate(batch_sentence, source=source_lang, target=target_lang, batch_size=32)
            else:
                res = mt_m2m100.translate(batch_sentence,source=source_lang,target=target_lang,batch_size=32)
            result.extend(res)
            torch.cuda.empty_cache()
        # sentence_ids = [{'index':index,'split_index':_[0],'sent_index':_[1]} for index,_ in enumerate(sentence_ids)]
        # sentence_ids.sort(key=itemgetter('split_index'))
        # res_list = []
        # for sent_index, data in groupby(sentence_ids, key=itemgetter('split_index')):
        #     res_list.append(''.join(result[x['index']] for x in data))
            # res_list.append({"index": sent_index, "value": ''.join(result[x['index']] for x in data)})
        output = []
        for index, mask in enumerate(doc_mask):
            if mask == 0:
                output.append(doc_split[index])
            else:
                sent = ''.join([result[index_res] for index_res, item in enumerate(sentence_ids) if item[0] == index])
                output.append(sent)
        output = ''.join(output)
        output = output.replace('<unk>','')
        # if target_lang =='Chinese':
        #     res = convert_traditional_2_simple_chinese(output)
        #     return res
        response = Response(response=json.dumps({"message":"success",
                                                 "results": output,"status":0}, ensure_ascii=False),
                            status=200,
                            mimetype="application/json")
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        print(type(response))
        return response
    except AssertionError:
        # traceback.print_exc()
        return Response(response=json.dumps({"message": "error",
                                             "result": "Please use the correct source language and target language.",
                                             "status": -3}),
                        status=200,
                        mimetype="application/json")
    except TypeError:
        return Response(response=json.dumps({"message": "error",
                                             "result": "Please use the correct parameter type.",
                                             "status": -2}),
                        status=200,
                        mimetype="application/json")
    except ParamterException:
        return Response(response=json.dumps({"message": "error",
                                             "result": "When using the traditional-simplified conversion service, please use \"Chinese\" as the target language",
                                             "status": -5}),
                        status=200,
                        mimetype="application/json")
    except:
        torch.cuda.empty_cache()
        traceback.print_exc()
        return Response(response=json.dumps({"message":"error",
                                             "result":"Error during translating",
                                             "status":-1}),
                        status=200,
                        mimetype="application/json")

@apps.route('/translate', methods=['POST'])
def translate():
  p = json.loads(request.get_data())
  article =p['text']
  source_lang = p['src']
  target_lang = p['dest']

  translate(article, source_lang, target_lang)


if __name__ == '__main__':
    apps.run(host='0.0.0.0',port='7000',debug=False,threaded=True)