#!/usr/bin/env python
# coding: utf-8

# ## Window에 bert 설치하기

# 0. python 가상환경 만들기 --> python -m venv 가상환경이름
# 
# 1. 깃 클론 진행 -> 이때, 설치 경로 상에 한글이 없도록 하기
# ```
# git clone https://github.com/SKTBrain/KoBERT.git
# cd KoBERT
# ```
# 
# 2. 다음의 주소를 참고해서 의존성 처리하기
# https://github.com/SKTBrain/KoBERT/issues/80
# - 일단, mxnet을 제외한 나머지 다운
# - 이후, mxnet을 별도로 다운
# - kobert 내부 py를 바깥으로 복사하기
# - pip install numpy==1.23진행
# 
# 3. python pytorch_kobert를 진행하기
# 
# 4. import 해서 확인하기

# In[1]:


import torch
from kobert.utils import get_tokenizer


# In[2]:


from kobert.pytorch_kobert import get_pytorch_kobert_model


# In[3]:


bertmodel, vocab = get_pytorch_kobert_model()


# In[4]:


device = torch.device("cuda:0")


# In[5]:


import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np
from tqdm import tqdm, tqdm_notebook


# In[6]:


import pandas as pd
data = pd.read_csv("sample_data.csv")


# In[7]:


data_list = list()
for sen, lab in zip(data["0"], data["1"]):
    data_list.append([sen,lab])


# In[8]:


data_list[:10]


# In[9]:


from sklearn.model_selection import train_test_split


# In[10]:


train_set, test_set = train_test_split(data_list, test_size=0.25, random_state=0) # train : test = 4 : 1


# In[11]:


len(train_set), len(test_set)


# In[12]:


class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len, pad, pair):

        # sentence , label data를 BERT의 입력값에 맞게 변환하는 transformer를 생성
        transform = nlp.data.BERTSentenceTransform(bert_tokenizer, max_len, pad=pad, pair=pair)

        ## 생성한 transformer로 sentence를 변환하여 저장
        self.sentences = [transform([data[sent_idx]]) for data in dataset]
        self.labels = [np.int32(data[label_idx]) for data in dataset]

    def __getitem__ (self, i):
        return (self.sentences[i] + (self.labels[i], )) # 각 index에 맞는 item 반환 진행 --> 왜 이런 형태인지는 잘 모르겠음

    def __len__(self):
        return (len(self.labels))


# In[13]:


# Parameter setting 진행
max_len = 64
batch_size = 64
warmup_ratio = 0.1
num_epochs = 5
max_grad_norm = 1
log_interval = 200
learning_rate =  5e-5


# In[14]:


# Kobert 모듈에서 제공하는 get_tokenizer와 vocab를 활용해 tokneizer를 구성한다
tokenizer = get_tokenizer() 
tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)

data_train = BERTDataset(train_set, 0, 1, tok, max_len, True, False)
data_test = BERTDataset(test_set, 0, 1, tok, max_len, True, False)
data_train[0]


# In[15]:


# Torch에 맞게 최종 입력 dataset 구성 

train_dataloader = torch.utils.data.DataLoader(data_train, batch_size=batch_size, num_workers=5)
test_dataloader = torch.utils.data.DataLoader(data_test, batch_size=batch_size, num_workers=5)


# In[16]:


class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size = 768, num_classes=4, dr_rate=None, params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        ## classifier는 선형 회귀 모델로 구성 (input size = 768, output size = 4 (label이 4개로 구성))
        self.classifier = nn.Linear(hidden_size, num_classes)

        ## overfitting 방지를 위한 dropout 비율 설정
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    # attention mask sequence를 구성해주는 함수 --> padding이 아닌 영역을 0에서 1로 변경
    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i,v in enumerate(valid_length):
            attention_mask[i][:v] = 1

        return attention_mask.float()

    # bert + classifier를 관통하는 forward 연산 진행
    def forward(self, token_ids, valid_length, segment_ids):

        # attention_mask 계산
        attention_mask = self.gen_attention_mask(token_ids, valid_length)

        # bert에 input 투입, 변수명이 pooler인거 보니 출력 embedding에 mean pooling 적용한 값이지 않을까 추측
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))

        # dropout 비율이 존재한다면, dropout 적용
        if self.dr_rate:
            out = self.dropout(pooler)

        # classifier 진행
        return self.classifier(out) 


# In[17]:


from transformers import AdamW
from transformers.optimization import get_cosine_schedule_with_warmup


# In[18]:


# Kobert + classifier 불러오기
model = BERTClassifier(bertmodel, dr_rate=0.3).to(device)

# optimizer (Adam), scheduler 설정
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate)
loss_fn = nn.CrossEntropyLoss()

t_total = len(train_dataloader) * num_epochs
warmup_step = int(t_total * warmup_ratio)

scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_step, num_training_steps=t_total)

#정확도 측정을 위한 함수 정의
def calc_accuracy(X,Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().data.cpu().numpy()/max_indices.size()[0]
    return train_acc
    
train_dataloader


# In[ ]:

def train():
    for e in range(1):

        train_acc = 0.0
        test_acc = 0.0
        model.train()

        # train set
        print("start")
        for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(train_dataloader)):
            optimizer.zero_grad()
            token_ids = token_ids.long().to(device)
            segment_ids = segment_ids.long().to(device)
            valid_length= valid_length
            label = label.long().to(device)
            
            # forward 연산 진행
            out = model(token_ids, valid_length, segment_ids)
            # loss 는 CrossEntropyLoss를 이용 -> backpropagation 학습 진행
            loss = loss_fn(out, label)
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
            optimizer.step()

            scheduler.step()  # Update learning rate schedule

            # train data set 정확도 확인
            train_acc += calc_accuracy(out, label)
            if batch_id % log_interval == 0:
                print("epoch {} batch id {} loss {} train acc {}".format(e+1, batch_id+1, loss.data.cpu().numpy(), train_acc / (batch_id+1)))
        print("epoch {} train acc {}".format(e+1, train_acc / (batch_id+1)))
        
        model.eval()

        # test set
        for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(test_dataloader)):
            token_ids = token_ids.long().to(device)
            segment_ids = segment_ids.long().to(device)
            valid_length= valid_length
            label = label.long().to(device)
            out = model(token_ids, valid_length, segment_ids)
            
            # test set 정확도 확인
            test_acc += calc_accuracy(out, label)
        print("epoch {} test acc {}".format(e+1, test_acc / (batch_id+1)))

if __name__ =='__main__':
    train()


# In[ ]:




