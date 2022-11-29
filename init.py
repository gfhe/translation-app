# from ltp import LTP
# import dl_translate as dlt
#
# ltp = LTP(pretrained_model_name_or_path='LTP/small')
# mt_m2m100 = dlt.TranslationModel(model_or_path='facebook/m2m100_418M',model_family='m2m100',device='cpu')
# mt_mbart50 = dlt.TranslationModel(model_or_path='facebook/mbart-large-50-many-to-many-mmt',model_family='mbart50',device='cpu')

import os
import huggingface_hub as hub

cache_dir = os.getenv('HUGGINGFACE_HUB_CACHE', '/root/.cache/huggingface/hub')
ltp_dir = hub.snapshot_download("LTP/small")
m2m100_dir = hub.snapshot_download("facebook/m2m100_418M")
# mbart_dir = hub.snapshot_download("facebook/mbart-large-50-many-to-many-mmt")
os.rename(ltp_dir, cache_dir + "/TLP__small")
os.rename(m2m100_dir, cache_dir + "facebook__m2m100_418M")
# os.rename(mbart_dir,cache_dir+"/facebook__m2m100_418M")
