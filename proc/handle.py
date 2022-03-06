#!/usr/bin/python
import json,os
from functools import reduce

data_fn_simp = os.path.join('idiom_simp.json')
with open(data_fn_simp) as fo:
    idiom_data = json.loads(fo.read())

def filter_shengdiao(data,include='0000',exclude='0000',show=False):
# input para:
#     data: idiom data
#     include: the right shengdiao at this position
#     exclude: shengdiao included in the idiom but not at this position
# caution: shengdiao neither in 'include' nor in 'exclude' is considered to be not in the idiom, so use a idiom with all four shengdiaos in your first try.
    count = 0
    for chengyu in data:
        sd = chengyu['shengdiao']
        # check char number, must be 4
        if len(sd) != 4:
            continue
        # check shengdiao of each char
        flag = True
        for i in range(4):
            isd = sd[i]
            if include[i] != '0' and isd != include[i]:
                flag = False
                break
            if isd == exclude[i]:
                flag = False
                break
            if not isd in include+exclude:
                flag = False
                break
            iex = exclude[i]
            if iex != '0' and iex not in sd:
                flag = False
                break
        if not flag: continue
        count += 1
        if show and count<1000: print('%03d'%count,chengyu['word'],'%6s%6s%6s%6s'%tuple(chengyu['pinyin']))
        yield chengyu

def filter_shengmuyunmu(data,exclude=[],position_include=[[],[],[],[]],position_exclude=[[],[],[],[]],show=False):
# input para:
#     data: idiom data
#     exclude: the idiom did not contain these shengmu/yunmu 
#     position_include: the shengmu/yunmu at the specific position
#     position_exclude: the idiom contain these shengmu/yunmu but not at this position
    count = 0
    for chengyu in data:
        sm = chengyu['shengmu']
        ym = chengyu['yunmu']
        # check char number, must be 4
        if len(sm) != 4:
            continue
        flag = True
        for i in range(4):
            if (sm[i] in exclude) or (ym[i] in exclude)\
              or (sm[i] in position_exclude[i]) or (ym[i] in position_exclude[i])\
              or (position_include[i] and (position_include[i] not in [sm[i],ym[i]])):
                # print(chengyu['word'],sm[i],ym[i],exclude,position_exclude[i],position_include[i])
                flag = False
                break
        if not flag: continue
        for smym in reduce(lambda x,y: x+y, position_exclude):
            if smym not in sm+ym:
                # print(chengyu['word'],smym,sm+ym)
                flag = False
                break
        if not flag: continue
        count += 1
        if show and count<1000: print('%03d'%count,chengyu['word'],'%6s%6s%6s%6s'%tuple(chengyu['pinyin']))
        yield chengyu
def filter_hanzi(data,hanzi,position=0,show=False):
# input para: only one hanzi is supported
#     data: idiom data
#     hanzi: hanzi
#     position: int, use 1-4 to represent the position of the hanzi, 0 for dont know.
    count = 0
    for chengyu in data:
        # check char number, must be 4
        if len(chengyu['word']) != 4:
            continue
        if position == 0:
            if hanzi in chengyu['word']:
                count += 1
                if show and count<1000: print('%03d'%count,chengyu['word'],'%6s%6s%6s%6s'%tuple(chengyu['pinyin']))
                yield chengyu
        else:
            if hanzi == chengyu['word'][position-1]:
                count += 1
                if show and count<1000: print('%03d'%count,chengyu['word'],'%6s%6s%6s%6s'%tuple(chengyu['pinyin']))
                yield chengyu
# test
test = False
if test:
    result1 = list(filter_shengdiao(idiom_data,include='0004',exclude='3120',show=True))
    result2 = list(filter_shengdiao(result1,include='1234',show=True))
    result3 = list(filter_shengmuyunmu(result2,exclude=['w','u','g','uang','i','s','e'],position_include=[[],[],[],[]],position_exclude=[[],[],['sh'],[]],show=True))
    result4 = list(filter_shengmuyunmu(result3,exclude=['j','ing','en','m','an','u'],position_include=[[],[],[],[]],position_exclude=[[],['sh'],[],['f']],show=True))
    result2a = list(filter_hanzi(result1,hanzi='一',show=True))
    result2b = list(filter_hanzi(result1,hanzi='一',position=3,show=True))   



print('***** Solving Handle(Chinese Wordle) *****')
print('notice: must contain all 4 shengdiaos in your first try.')
print('''Input:
shengdiao: a four digital number with "1" "2" "3" "4" represents shengdiao of each char. Input grey directly, add "-" before orange, add '+' before green. Use enter to skip.
shengmu/yunmu: input all the 8 shengmu/yunmu with one space (' ') as the delimiter, input two spaces if a char has no shengmu. Input grey directly, add '-' before orange, add '+' before green. Use enter to skip.
hanzi: input ONE included hanzi and its right position(if has)， with space as the delimeter. Use enter to skip.

example:
    correct answer: 风调雨顺
    first guess: 五光十色
        shengdiao: -3-1-2+4
        shengmu/yunmu: w u g uang -sh i s e
        hanzi: (enter to skip)
    second guess: 精神满腹
        shengdiao: +1+2+3+4
        shengmu/yunmu: j ing -sh en m an -f u
        hanzi: (enter to skip)
    you will get the filtered chengyu:
        001 飞禽走兽    fēi   qín   zǒu  shòu
        002 风调雨顺   fēng  tiáo    yǔ  shùn
''')

result = idiom_data
while(True):
    sd_raw = input('shengdiao: ')
    if sd_raw:
        lsd = list(sd_raw)
        lsd.reverse()
        inc = ''
        exc = ''
        while(True):
            try:
                ch = lsd.pop()
            except Exception as e:
                break
            if ch == '+':
                inc += lsd.pop()
                exc += '0'
            elif ch == '-':
                inc += '0'
                exc += lsd.pop()
            else:
                inc += '0'
                exc += '0'
        result = list(filter_shengdiao(result,include=inc,exclude=exc,show=True))

    sy_raw = input('shengmu/yunmu: ')
    if sy_raw:
        lsy = sy_raw.split(' ')
        lsy.reverse()
        exc = []
        pinc = [[],[],[],[]]
        pexc = [[],[],[],[]]
        for i in range(4):
            for j in range(2):
                sy = lsy.pop()
                if sy:
                    if sy[0] == '-':
                        pexc[i] += [sy[1:]]
                    elif sy[0] == '+':
                        pinc[i] += [sy[1:]]
                    else:
                        exc += [sy]
        result = list(filter_shengmuyunmu(result,exclude=exc,position_include=pinc,position_exclude=pexc,show=True))

    hz_raw = input('hanzi汉字: ')
    if hz_raw:
        lhz = hz_raw.split(' ')
        hz = lhz[0]
        if len(lhz) == 2:
            pos = lhz[1]
        else:
            pos = 0
        result = list(filter_hanzi(result,hanzi=hz,position=pos,show=True))
    
    if not (sd_raw or sy_raw or hz_raw):
        break