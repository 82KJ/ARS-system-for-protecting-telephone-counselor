import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np

from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model

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


class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size = 768, num_classes=3, dr_rate=None, params=None):
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

class KoBERT:
    def __init__(self):
        print("모델 init 시작")
        self.device = 'cpu'
        self.max_len = 64
        self.batch_size = 64
        self.bertmodel, self.vocab = get_pytorch_kobert_model()
        self.tokenizer = get_tokenizer() 
        self.tok = nlp.data.BERTSPTokenizer(self.tokenizer, self.vocab, lower=False)

        self.model = BERTClassifier(self.bertmodel, dr_rate=0.5).to(self.device)
        self.model_state_dict = torch.load("C:\\Users\\penpenguin2018\\ARS-system-for-protecting-telephone-counselor\\MS\\study\\main\\kobert_classifier.pth", map_location=self.device)
        self.model.load_state_dict(self.model_state_dict)
        print("모델 init 완료")


    def predict(self, predict_sentence):

        # 1. data set 구성 (문장, 라벨)
        data = [predict_sentence, '0']
        dataset_another = [data]

        # 2. data를 bert의 입력에 맞게 변환하기
        another_test = BERTDataset(dataset_another, 0, 1, self.tok, self.max_len, True, False)
        test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=self.batch_size, num_workers=0)
        
        self.model.eval()

        for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
            token_ids = token_ids.long().to(self.device)
            segment_ids = segment_ids.long().to(self.device)
            valid_length= valid_length
            label = label.long().to(self.device)

            # 모델 forward 연산 진행
            out = self.model(token_ids, valid_length, segment_ids)

            # torch out -> numpy 형식으로 변환
            test_eval=[]
            logits = out[0].detach().cpu().numpy()
            
            # 값이 가장 큰 인덱스를 출력
            if np.argmax(logits) == 0:
                test_eval= "일반"
            elif np.argmax(logits) == 1:
                test_eval = "폭언"
            elif np.argmax(logits) == 2:
                test_eval = "성희롱"
            
            return test_eval


            #print(">> " + test_eval + " 문장입니다.")