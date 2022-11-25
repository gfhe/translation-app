from ltp import LTP
import nltk
import re
import dl_translate as dlt

ltp = LTP(pretrained_model_name_or_path='LTP/small')
mt_m2m100 = dlt.TranslationModel(model_or_path='facebook/m2m100_418M',model_family='m2m100',device='cpu')
mt_mbart50 = dlt.TranslationModel(model_or_path='facebook/mbart-large-50-many-to-many-mmt',model_family='mbart50',device='cpu')