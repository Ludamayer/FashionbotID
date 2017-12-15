from flask import Flask, request, jsonify
import json
import re
import requests
import pandas as pd
from pandas import DataFrame

app = Flask(__name__)

csvfile = pd.read_csv('keyword.csv')
csvf = DataFrame(csvfile, columns=["number", "text", "url"])
csvframe = csvf.set_index("number")
searcher = csvframe["text"]  ## searcher.loc[code] code 값에 인덱스 값을 집어 넣을 것.
photourl = csvframe["url"]  ## photourl.loc[code] code 값에 인덱스 값 넣기

##버튼 제작용 변수입니다. c뒤의 숫자는 상위개념의 해당 인덱스입니다. (아우터의 경우 c0의 0번이므로 c00 이런식)

c000_type = [u"1.남자", u"2.여자"]
c100_type = ["A:아우터", "B:상의", "C:하의", "D:원피스"]  ##대분류. 남자용은 0-2번만 사용.
c110_type = ["A:점퍼", "B:자켓", "C:코트", "D:베스트", "E:가디건"]  ##소분류-아우터.
c120_type = ["A:셔츠", "B:티셔츠", "C:니트", "D:블라우스"]  ## 소분류-상의. 남자용은 0-2번만 사용
c130_type = ["A:팬츠", "B:트레이닝", "C:스커트"]  ##소분류-하의. 남자용은 0-1번만.
c111_type = ["1.후드집업", "2.패딩", "3.항공점퍼", "4.야구점퍼"]  ##아우터-점퍼.
c112_type = ["1.청(데님)", "2.야상", "3.라이더", "4.블레이저", "5.블루종", "6.필드", "7.볼레로"]  ##아우터-자켓. 남자는 0-5,
c113_type = ["1.케이프", "2.트렌치", "3.더플", "4.맥(발마칸)", "5.피", "6.체스터필드", "7.브리티쉬웜"]  ##아우터-코트. 여자는 0-5
c114_type = ["1.니트", "2.패딩", "3.퍼", "4.밍크"]  ##아우터-베스트. 남자는 0-2
c115_type = ["1.가디건"]  ##아우터-가디건.
c121_type = ["1.와이셔츠", "2.청셔츠"]  ##상의-셔츠.
c122_type = ["1.티셔츠", "2.후드티", "3.맨투맨"]  ##상의-티셔츠.
c123_type = ["1.스웨터"]  ##상의-니트.
c124_type = ["1.블라우스"]  ##상의-블라우스.
c131_type = ["1.청(데님)", "2.면", "3.정장", "4.슬랙스", "5.멜빵", "6.카고"]  ##하의-팬츠.
c132_type = ["1.트레이닝", "2.조거팬츠"]  ##하의-트레이닝.
c133_type = ["1.트임", "2.테니스", "3.플레어", "4.플리츠", "5.정장"]  ##하의-스커트.
c140_type = ["1.기본", "2.레이어드", "3.정장", "4.점프수트"]  ## 원피스
selector_type = ["네. 이걸로 할게요","좀 더 자세히 찾아볼래요", "처음부터 다시 찾아볼래요"]
select_naver = ["네. 이걸로 할게요", "다르게 검색해 볼래요"]


def getText(text, button):  ## 글만 띄워주는 메시지창
    t_message = {
        "message": {"text": str(text)},
        "keyboard": {"type": "buttons", "buttons": button}
    }
    return t_message


def getPhoto(text, purl, width, height, button):  ## 사진도 함께 띄워주는 메시지창
    p_message = {
        "message": {
            "text": str(text),
            "photo": {
                "url": purl, "width": width, "height": height
            }
        },
        "keyboard": {"type": "buttons", "buttons": button}
    }
    return p_message


def getNaver(text, purl, link, button):
    s_message = {
        "message": {
            "text": str(text),
            "photo": {
                "url": purl, "width": 480, "height": 480
            },
            "message_button": {
                "label": "쇼핑몰 링크로 이동",
                "url": link
            }
        },
        "keyboard": {"type": "buttons", "buttons": button}
    }
    return s_message


database = {}

s_question = "성별을 선택해 주세요."
a_question = "큰 분류사항을 선택해 주세요."
b_question = "세부 분류사항을 선택해 주세요."
c_question = "사진을 보시고 맘에 드는것을 골라보세요."
d_question = "이것으로 할까요?"


#################################################################

def Selector(content,user_key):
    if content == u"1.남자":
        database[user_key][0][0] = 1
        datasend = getText(a_question, c100_type[0:3])
    elif content == u"2.여자":
        database[user_key][0][0] = 2
        datasend = getText(a_question, c100_type)

    return datasend


##성별을 선택하고, 남자의 경우 아우터/상의/하의만 선택할 수 있게 보냅니다.

def SSelector(content,user_key):
    global database
    if content == c100_type[0]:
        database[user_key][0][1] = 1
        datasend = getText(b_question, c110_type)
    elif content == c100_type[1] and database[user_key][0][0] == 1:
        database[user_key][0][1] = 2
        datasend = getText(b_question, c120_type[0:3])
    elif content == c100_type[1] and database[user_key][0][0] == 2:
        database[user_key][0][1] = 2
        datasend = getText(b_question, c120_type)
    elif content == c100_type[2] and database[user_key][0][0] == 1:
        database[user_key][0][1] = 3
        datasend = getText(b_question, c130_type[0:2])
    elif content == c100_type[2] and database[user_key][0][0] == 2:
        database[user_key][0][1] = 3
        datasend = getText(b_question, c130_type)
    elif content == c100_type[3]:
        database[user_key][0][1] = 4
        database[user_key][0][2] = 1
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c140_type)

    return datasend


## 대분류를 정할수 있게 나눠줍니다. 원피스는 소분류가 없으므로 바로 값을 최종으로 넘겨줍니다.

def ASelector(content,user_key):
    global database
    if content == c110_type[0]:
        database[user_key][0][2] = 1
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question+user_key, purl, 480, 480, c111_type[0:6])
    elif content == c110_type[1] and database[user_key][0][0] == 1:
        database[user_key][0][2] = 2
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 720, c112_type[0:6])
    elif content == c110_type[1] and database[user_key][0][0] == 2:
        database[user_key][0][2] = 2
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 960, c112_type)
    elif content == c110_type[2] and database[user_key][0][0] == 1:
        database[user_key][0][2] = 3
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 960, c113_type)
    elif content == c110_type[2] and database[user_key][0][0] == 2:
        database[user_key][0][2] = 3
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 720, c113_type[0:6])
    elif content == c110_type[3] and database[user_key][0][0] == 1:
        database[user_key][0][2] = 4
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c114_type[0:3])
    elif content == c110_type[3] and database[user_key][0][0] == 2:
        database[user_key][0][2] = 4
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c114_type)
    elif content == c110_type[4]:
        database[user_key][0][2] = 5
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c115_type)

    return datasend


## 아우터류를 선택할 수 있게 해줍니다.

def BSelector(content,user_key):
    global database
    if content == c120_type[0]:
        database[user_key][0][2] = 1
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 240, c121_type)
    elif content == c120_type[1]:
        database[user_key][0][2] = 2
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c122_type)
    elif content == c120_type[2]:
        database[user_key][0][2] = 3
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c123_type)
    elif content == c120_type[3]:
        database[user_key][0][2] = 4
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 480, c124_type)

    return datasend


## 상의류를 선택할 수 있게 해줍니다.

def CSelector(content,user_key):
    global database
    if content == c130_type[0]:
        database[user_key][0][2] = 1
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 720, c131_type)
    elif content == c130_type[1]:
        database[user_key][0][2] = 2
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 240, c132_type)
    elif content == c130_type[2]:
        database[user_key][0][2] = 3
        purl = PhotoSearch(database[user_key][0])
        datasend = getPhoto(c_question, purl, 480, 720, c133_type)

    return datasend


## 하의류를 선택할 수 있게 해줍니다.

def FinalSelector(content,user_key, button):
    count = 0
    global database
    for i in button:
        count += 1
        if content == i:
            database[user_key][0][3] = count
            purl = PhotoSearch(database[user_key][0])
            name = NameSearch(database[user_key][0])
            datasend = getPhoto("찾는 것이 " + name + "인가요?", purl, 480, 600, selector_type)

    return datasend


## 최종 선택을 사진과 함께 할 수 있도록 도와줍니다.

def PhotoSearch(tester):
    ixnum = int("".join(map(str, tester)))
    purl = photourl.loc[ixnum]
    return purl


## 사진을 찾게 해 줍니다.

def NameSearch(tester):
    ixnum = int("".join(map(str, tester)))
    name = searcher.loc[ixnum]
    return name


## 이름을 찾게 해 줍니다.

def NaverSearch(name,user_key):
    global database
    pw = "I0wsPNZOrz"  ## naverAPI 접근 패스워드입니다.
    item = str(name)  ## 품목명을 받습니다.
    url = "https://openapi.naver.com/v1/search/shop.json"  ## API url
    headers = {"X-Naver-Client-Id": "TuLmh9xSA6B3412jC2f1", "X-Naver-Client-Secret": pw}  ##헤더
    params = {"query": item, "display": 3}  ##패러미터. 쿼리쪽에 이름이 들어가고 3개만 받아옵니다.
    rs = requests.get(url, headers=headers, params=params).json()  ## 리퀘스트 합니다.(get)
    rg = r"[가-힣]+"
    f_list = []

    for i in range(3):
        a = [" ".join(re.findall(rg, rs["items"][i]['title'])), rs["items"][i]["lprice"], rs["items"][i]["image"],
             rs["items"][i]["link"]]
        f_list.append(a)
        database[user_key][3][i] = " ".join(re.findall(rg, rs["items"][i]['title']))

    return f_list


## 네이버 API를 이용해 정보를 받아옵니다.

def AskNaver(user_key):
    global database
    name = NameSearch(database[user_key][0])
    if database[user_key][0][0] == 1:
        s_type = "남자"
    elif database[user_key][0][0] == 2:
        s_type = "여자"

    database[user_key][2] = NaverSearch(s_type+" "+database[user_key][1]+" "+name,user_key)

    datasend = getText("검색이 완료되었습니다. 정보를 보고싶은 제품을 선택해 보세요.", database[user_key][3])

    return datasend


## 추가로 받을 질문을 받습니다

def AnswerNaver(content,user_key):
    global database
    j = database[user_key][3].index(content)
    njs = database[user_key][2][j]
    datasend = getNaver(njs[0] + "\n" + njs[1] + "원", njs[2], njs[3], database[user_key][3])

    return datasend


## API에서 받은 정보를 출력해 줍니다.

##############################실제 실행 구역#############################################

@app.route('/keyboard')
def keyboard():  ## 기본 키보드 관련
    datasend = {
        "type": "buttons",
        "buttons": ["챗봇 시작"]
    }
    return jsonify(datasend)


@app.route('/message', methods=['POST'])
def message():  ## 실제 메시지 부
    data = request.get_json()
    content = data['content']
    user_key = data['user_key']

    global database
    if content == u"챗봇 시작":
        database[user_key] = [[0, 0, 0, 0], "", [],["결과없음", "결과없음", "결과없음", "처음부터 다시 찾아볼래요"]]
        datasend = getText(s_question, c000_type)

    elif content in (c000_type):  ## 성별을 받았을 때
        datasend = Selector(content,user_key)
    elif content in (c100_type):  ## 대분류중 하나를 받았을 때
        datasend = SSelector(content,user_key)
    elif content in (c110_type):  ## 대분류 중 아우터 받았을 경우
        datasend = ASelector(content,user_key)
    elif content in (c120_type):  ## 대분류 중 상의 받았을 경우
        datasend = BSelector(content,user_key)
    elif content in (c130_type):  ## 대분류 중 하의 받았을 경우
        datasend = CSelector(content,user_key)

    elif content in (c111_type):  ## 아우터 - 코트를 받았을 때
        datasend = FinalSelector(content,user_key, c111_type)
    elif content in (c112_type):  ##
        datasend = FinalSelector(content,user_key, c112_type)
    elif content in (c113_type):
        datasend = FinalSelector(content,user_key, c113_type)
    elif content in (c114_type):
        datasend = FinalSelector(content,user_key, c114_type)
    elif content in (c115_type):
        datasend = FinalSelector(content,user_key, c115_type)

    elif content in (c121_type):
        datasend = FinalSelector(content,user_key, c121_type)
    elif content in (c122_type):
        datasend = FinalSelector(content,user_key, c122_type)
    elif content in (c123_type):
        datasend = FinalSelector(content,user_key, c123_type)
    elif content in (c124_type):
        datasend = FinalSelector(content,user_key, c124_type)

    elif content in (c131_type):
        datasend = FinalSelector(content,user_key, c131_type)
    elif content in (c132_type):
        datasend = FinalSelector(content,user_key, c132_type)
    elif content in (c133_type):
        datasend = FinalSelector(content,user_key, c133_type)

    elif content in (c140_type):
        datasend = FinalSelector(content,user_key, c140_type)

    elif content == "처음부터 다시 찾아볼래요":
        datasend = getText(s_question, c000_type)
        database[user_key] = [[0, 0, 0, 0], "", [],["결과없음", "결과없음", "결과없음", "처음부터 다시 찾아볼래요"]]

    elif content == selector_type[1]:
        datasend = {"message": {"text": "세부적으로 검색하고 싶으신 특성이 있으신가요? 있으시다면 기입해 주세요.\n(재질, 기장, 핏 등)"}}

    elif content == "다르게 검색해 볼래요":
        database[user_key][1] = ""
        database[user_key][2] = []
        datasend = {"message": {"text": "세부적으로 검색하고 싶으신 특성이 있으신가요? 있으시다면 기입해 주세요.\n(재질, 기장, 핏 등)"}}

    elif content == select_naver[0]:
        datasend = AskNaver(user_key)

    elif content in (database[user_key][3][0:3]):
        datasend = AnswerNaver(content,user_key)

    else:
        item_name = NameSearch(database[user_key][0])
        datasend = getText("<" + content + " " + item_name + ">" + "단어로 검색할까요?", select_naver)
        database[user_key][1] += content

    return jsonify(datasend)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6015)