#!/usr/bin/python
from chengyu_pinyin_tools import *

with open(chengyu_pinyin().data_simp_fn) as fo:
    idiom_data = json.loads(fo.read())

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
count = 0
while(True):
    count += 1
    print('Round %d'%count)

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
        result = list(chengyu_pinyin.filter_shengdiao(result,include=inc,exclude=exc,show=True)) 
    if len(result) < 2:
        print('*** Nothing left, restart. ***')
        result = idiom_data
        count = 0
        continue

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
        result = list(chengyu_pinyin.filter_shengmuyunmu(result,exclude=exc,position_include=pinc,position_exclude=pexc,show=True))
    if len(result) < 2:
        print('*** Nothing left, restart. ***')
        result = idiom_data
        count = 0
        continue

    hz_raw = input('hanzi汉字: ')
    if hz_raw:
        lhz = hz_raw.split(' ')
        hz = lhz[0]
        if len(lhz) == 2:
            pos = lhz[1]
        else:
            pos = 0
        result = list(chengyu_pinyin.filter_hanzi(result,hanzi=hz,position=pos,show=True))
    if len(result) < 2:
        print('*** Nothing left, restart. ***')
        result = idiom_data
        count = 0
        continue

    
    if not (sd_raw or sy_raw or hz_raw):
        break