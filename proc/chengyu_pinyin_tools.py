#!/usr/bin/python
import json,os,sys
from functools import reduce

# path parameter
abspath,fn = os.path.split(os.path.abspath(sys.argv[0]))
root,path = os.path.split(abspath)

class pinyin:
    # basic data #
    __shengmu = ('b','p','m','f','d','t','n','l','g','k','h','j','q','x','r','w','y','z','c','s','zh','ch','sh')
    __yunmu = ('ang','eng','ing','ong','an','en','in','un','ai','ei','ao','ou','iu','er','en','a','o','e','i','u', 'v')
    __shengdiao = {'a':['ā','á','ǎ','à'],'o':['ō','ó','ǒ','ò'],'e':['ē','é','ě','è'],'i':['ī','í','ǐ','ì'],'u':['ū','ú','ǔ','ù'],'v':['ǖ','ǘ','ǚ','ǜ']}
    # 当j、q、x、y与ü相拼时，要去掉两点。
    __shengdiao_jqxy = {'a':['ā','á','ǎ','à'],'o':['ō','ó','ǒ','ò'],'e':['ē','é','ě','è'],'i':['ī','í','ǐ','ì'],'v':['ū','ú','ǔ','ù']}
    __shengdiao_inv = {'ā': ['a', 1], 'á': ['a', 2], 'ǎ': ['a', 3], 'à': ['a', 4], 'ō': ['o', 1], 'ó': ['o', 2], 'ǒ': ['o', 3], 'ò': ['o', 4], 'ē': ['e', 1], 'é': ['e', 2], 'ě': ['e', 3], 'è': ['e', 4], 'ī': ['i', 1], 'í': ['i', 2], 'ǐ': ['i', 3], 'ì': ['i', 4], 'ū': ['u', 1], 'ú': ['u', 2], 'ǔ': ['u', 3], 'ù': ['u', 4], 'ǖ': ['v', 1], 'ǘ': ['v', 2], 'ǚ': ['v', 3], 'ǜ': ['v', 4]}
    __shengdiao_jqxy_inv = {'ā': ['a', 1], 'á': ['a', 2], 'ǎ': ['a', 3], 'à': ['a', 4], 'ō': ['o', 1], 'ó': ['o', 2], 'ǒ': ['o', 3], 'ò': ['o', 4], 'ē': ['e', 1], 'é': ['e', 2], 'ě': ['e', 3], 'è': ['e', 4], 'ī': ['i', 1], 'í': ['i', 2], 'ǐ': ['i', 3], 'ì': ['i', 4], 'ū': ['v', 1], 'ú': ['v', 2], 'ǔ': ['v', 3], 'ù': ['v', 4]}
    
    @property
    def shengmu(self):
        return self.__shengmu
    @property
    def yunmu(self):
        return self.__yunmu
    @property
    def shengdiao(self):
        return self.__shengdiao
    @property
    def shengdiao_jqxy(self):
        return self.__shengdiao_jqxy
    @property
    def shengdiao_inv(self):
        return self.__shengdiao_inv
    @property
    def shengdiao_jqxy_inv(self):
        return self.__shengdiao_jqxy_inv
    
    def __init__(self,regen_sd_inv=False):
        # The following code is actually useless, just to keep the code I used to generate '__shengdiao_inv'.
        if regen_sd_inv:
            for k in self.shengdiao:
                v = self.__shengdiao[k]
                for i in range(4):
                    self.__shengdiao_inv[v[i]] = [k,i+1]
            for k in self.shengdiao_jqxy:
                v = self.__shengdiao_jqxy[k]
                for i in range(4):
                    self.__shengdiao_jqxy_inv[v[i]] = [k,i+1]
    def shengdiao_convert(self,py,mode='auto'):
        if py[0] in 'jqxy':
            shengdiao = self.shengdiao_jqxy
            shengdiao_inv = self.shengdiao_jqxy_inv
        else:
            shengdiao = self.shengdiao
            shengdiao_inv = self.shengdiao_inv
        def sd2num(py):
            for i in range(len(py)):
                if py[i] in shengdiao_inv:
                    c,n = shengdiao_inv[py[i]]
                    return py.replace(py[i],c) + str(n)
            return py
        def num2sd(py):
            if py[-1] in '1234':
                for i in range(len(py)):
                    if py[i] in shengdiao:
                        c = shengdiao[py[i]][int(py[-1])-1]
                        return py.replace(py[i],c).replace(py[-1],'')
            return py
        if mode=='sd2num':
            return sd2num(py)
        elif mode=='num2sd':
            return num2sd(py)
        else:
            pyc = sd2num(py)
            if pyc==py:
                pyc = num2sd(py)
            return pyc
    def split(self,py,qingsheng=''):
        sm = ''
        ym = self.shengdiao_convert(py,mode='sd2num')
        sd = qingsheng
        if ym[-1] in '1234':
            sd = ym[-1]
            ym = ym[0:-1]
        if ym[0:2] in self.shengmu:
            sm = ym[0:2]
            ym = ym[2:]
        elif py[0:1] in self.shengmu:
            sm = ym[0:1]
            ym = ym[1:]
        return sm,ym,sd

class chengyu_pinyin(pinyin):
    __data_fn = os.path.join(root,'data','idiom.json')
    __data_simp_fn = os.path.join(root,path,'idiom_simp.json')
    
    @property
    def data_fn(self):
        return self.__data_fn
    @property
    def data_simp_fn(self):
        return self.__data_simp_fn
    
    def extract_pinyin_infos(self,data='',out=''):
        if not out:
            out = self.data_simp_fn
        if not data:
            data = self.data_fn
        if isinstance(data,str):
            with open(data) as fo:
                data = json.loads(fo.read())
        def detach(data_simp):
            for chengyu in data_simp:
                shengmu,yunmu,shengdiao = zip(*map(lambda x:pinyin().split(x,qingsheng='5'),chengyu['pinyin']))
                shengdiao = ''.join(shengdiao)
                chengyu['shengmu'] = shengmu
                chengyu['yunmu'] = yunmu
                chengyu['shengdiao'] = shengdiao
                if '55' in shengdiao: print(chengyu)
                yield chengyu
        idiom_data_simp = [{'word':item['word'],'pinyin':item['pinyin'].split()} for item in data]
        result = detach(idiom_data_simp)
        if out and not out == 'test':
            if os.path.isfile(out):
                choice = input('File exist "%s", continue? y/[n]'%out)
                if not 'y' in choice.lower():
                    return list(result)
            with open(out,'w') as fo:
                fo.write(json.dumps(list(result)))
                print('Saved to %s'%os.path.abspath(out))
        return list(result)

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
                or (position_include[i] and (''.join(position_include[i]) not in sm[i]+ym[i])):
                    # if (position_include[i] and (''.join(position_include[i]) not in sm[i]+ym[i])):
                    #     print(chengyu['word'],sm[i],ym[i],exclude,position_exclude[i],position_include[i])
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

if __name__=='__main__':
    print('*** test pinyin ***')
    print(pinyin().shengdiao_convert('jū'),pinyin().shengdiao_convert('jv3'),pinyin().shengdiao_convert('er'))
    print(pinyin().split('jū'),pinyin().split('shǔang'),pinyin().split('er',qingsheng='0'))
    pys = ['ē', 'dǎng', 'bǐ', 'zhou']
    shengmu,yunmu,shengdiao = zip(*map(lambda x:pinyin().split(x,qingsheng='5'),pys))
    shengdiao = ''.join(shengdiao)
    print(shengmu,yunmu,shengdiao)

    print('*** test chengyu_pinyin().extract_pinyin_infos ***')
    with open(chengyu_pinyin().data_fn) as fo:
        idiom_data = json.loads(fo.read())# load data #
    num = len(idiom_data)
    sample = idiom_data[1::num//10]
    num_sample = len(sample)
    print(sample[2])
    print(num,num_sample)
    print(chengyu_pinyin().extract_pinyin_infos(sample,out='test'))
    
    print('*** test filter ***')
    chengyu_pinyin().extract_pinyin_infos(idiom_data)
    with open(chengyu_pinyin().data_simp_fn) as fo:
        idiom_data = json.loads(fo.read())
    result1 = list(chengyu_pinyin.filter_shengdiao(idiom_data,include='0004',exclude='3120',show=True))
    result2 = list(chengyu_pinyin.filter_shengdiao(result1,include='1234',show=True))
    result3 = list(chengyu_pinyin.filter_shengmuyunmu(result2,exclude=['w','u','g','uang','i','s','e'],position_include=[[],[],[],[]],position_exclude=[[],[],['sh'],[]],show=True))
    result4 = list(chengyu_pinyin.filter_shengmuyunmu(result3,exclude=['j','ing','en','m','an','u'],position_include=[[],[],[],['sh','un']],position_exclude=[[],['sh'],[],['f']],show=True))
    result2a = list(chengyu_pinyin.filter_hanzi(result1,hanzi='一',show=True))
    result2b = list(chengyu_pinyin.filter_hanzi(result1,hanzi='一',position=3,show=True))   
