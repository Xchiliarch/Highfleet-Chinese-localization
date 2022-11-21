from genericpath import exists
from itertools import chain                 #not necessary for other languages 
from xpinyin import Pinyin                  #not necessary for other languages
import os
import re
import hashlib

p = Pinyin()                                #these functions are for chinese localization only,other languages do not need it
def to_pinyin(s):                           
    return ''.join(chain.from_iterable(p.get_pinyin(s, tone_marks='numbers') ))

def compare(file,texts):                    #compare the newly generated char set and old one,if different return 1
    f= open(file,'rb')              
    chars =  f.read()
    filemd5 = hashlib.md5(chars).hexdigest()
    textmd5 = hashlib.md5(texts.encode('utf-8')).hexdigest()
    if filemd5!=textmd5:
        return 1
    else:
        return 0

def find_all_chara_text(a,font_name):       #输出并返回所有文本出现的单字、符号,以unicode编码排序 all_char.txt  该文档用于检视所有单字与编码检索
    f= open(a,encoding='utf-8')             #return and save all used characters used as {fontscan}all_char.txt,sorted by unicode.
    texts = f.read()
    f.close()

    font =[]
    for text in texts:
        if( ord(text)  == 183 and text not in font):                #人名间隔号 ·
            font.append(text)
        if( ord(text)>3000 and text not in font):
            font.append(text)
    #font = sorted(font,key = to_pinyin)    #拼音排序
    font = sorted(font)                     #unicode编码排序 #sort by unicode

    print(f'{len(font)} chars',end=' ')      #统计字符数 #calculate all chars used

    all_char =''
    for item in font:
        all_char = all_char+item
    if os.path.exists('.\\int_files\\font') == False:       #if int_files folder not exist,create
        os.makedirs('.\\int_files\\font')
    if os.path.exists(f'.\\int_files\\font\\{font_name}all_char.txt'):              #check if {font_name}all_char.txt already exists,if exists,
        if compare(f'.\\int_files\\font\\{font_name}all_char.txt',all_char):        #message will pop to inform you that you need to redraw tex file
            print(f'字符集内字符发生改变，请重新绘制Tex')                   
            #print(f'{font_name} char set has changed,please redraw Tex file.')

    g = open(f'.\\int_files\\font\\{font_name}all_char.txt','w',encoding='utf-8')   #generate {font_name}all_char.txt to .\int_files\{font_name}all_char.txt
    g.write(all_char)
    g.close()
    return font

def output_font(text,row_num,font_name):  #单字输出到格式化文本 draw_char.txt. row_num 为一排字个数  该文档用于PS内绘制贴图
    out =''                               #generate {font_name}draw_char.txt  row-num is the number of char drawn per row in Photoshop or other softeware.           
    for i in range(len(text)):
        if(i%row_num==0 and i!=0):
            out = out+'\n'+text[i]
        else:
            out = out+text[i]
    if os.path.exists('.\\build\\Tex_Gen') == False:
        os.makedirs('.\\build\\Tex_Gen')
    f = open(f'.\\build\\Tex_Gen\\{font_name}draw_char.txt','w',encoding='utf-8')
    f.write(out)
    f.close()

name_lookup =[] 
def res_registration(font,tex_name,font_name,IcoorX,coorY,rectX,rectY,row_num):  #生成字库Res、字符编码对应集
    name_lookup.clear()                                                          #generate {tex_name}_{font_name}.res,this is the index for tex file to find chars in game.
    res = '\n'      #res is the string of res of each char 
    lookup = ''     #lookup is the string os each char's unique name in res                               
    for i in range(len(font)):                                      #traverse through all chars                                
        character = font[i]
        #print(character)
        name = p.get_pinyin(character, tone_marks='numbers')    #获取字符拼音    #get the pinyin of a chinese char. note that different chars may have the same pinyin,
                                                                                #but below has the solution to this : add number behind: like  cha4_0 and cha4_1 etc.

        if ord(character)>65280 or ord(character) <12291:       #because get_pinyin() cannot get the punctuations right so you have to manually set the name of each char.  
            if name == '·':
                name = 'jiange'                
            if name == '—':
                name = 'hengang'
            elif name == '‘':
                name = 'Ldanyinhao'
            elif name == '’':
                name = 'Rdanyinhao'
            elif name == '“':
                name = 'Lshuangyinhao'
            elif name == '”':
                name = 'Rshuangyinhao'
            elif name == '…':
                name = 'shenglvehao'
            elif name == '、':
                name = 'dunhao'
            elif name == '。':
                name = 'juhao'
            elif name == '！':
                name = 'gantanhao'
            elif name == '（':
                name = 'Lkuohao'
            elif name == '）':
                name = 'Rkuohao'
            elif name == '，':
                name = 'douhao'
            elif name == '：':
                name = 'maohao'
            elif name == '？':
                name = 'wenhao'

        j = 0
        while(1):                               #the way to avoid chars have same pinyin have the same name,by adding numbers behind.
            fname = name+f'_{j}'
            if fname not in name_lookup:
                name_lookup.append(fname)
                break
            j += 1                              #获取字符唯一编码名

        if(i%row_num==0 and i!=0):              #update coordinations of a char in tex file.
            coorY +=rectY
        coorX = (i%row_num)*rectX+IcoorX

        res =  res+(                                #the res of each char
            f"Animation {font_name}_{fname}\n"
            "{\n"
            f" texture = {tex_name}\n"
            f" rect = {coorX},{coorY},{rectX},{rectY}\n"
            f" hotspot = {rectX//2},{rectY//2}\n"
            f" zorder = 0.000000\n"
            f" resgroup = 0\n"
            f" frame = 1\n"
            "}\n"
        )                                           
        lookup = lookup+fname+'\n'                  #append char's unique name to lookup

    if os.path.exists('.\\int_files\\res') == False:
        os.makedirs('.\\int_files\\res')

    f = open(f'.\\int_files\\res\\{tex_name}_{font_name}.res','w',encoding='utf-8') #write res to file
    f.write(res)
    f.close()
    if os.path.exists('.\\int_files\\font') == False:
        os.makedirs('.\\int_files\\font')
    g = open(f'.\\int_files\\font\\{font_name}lookup.txt','w',encoding='utf-8')     #write lookup to file
    g.write(lookup)
    g.close()

def encode_gen(dialog,default_font):                             #通过chinese.txt生成编码后的english.txt，具有字体fallback机制 
    ds = os.listdir('.\\int_files\\font')        #using translated dialog to generate encoded english.txt which chars are translated to texture                                              
    
    fonts_name =[]          # all font's name as a list
    fallback =0             #fallback indicator, there may be new chars using non-default-fonts but non-default-fonts has not yet added that char.but if
    i=0                     # default font contain that char ,this function can detect that and make that char fall back to default font.

    for d in ds:                                
        a = re.match('(.*?)lookup.txt',d)       
        if(a):
            fonts_name.append(a.groups()[0])
            i+= 1                               #read all font used and save their names in fonts_name

    for name in fonts_name:                     #traverse through every font
        f= open(f'.\\int_files\\font\\{name}all_char.txt',encoding='utf-8')   #      
        locals()[f'{name}texts'] = f.read()                     #eg:if a font's name is MC20, this variable's name is MC20texts,and it's the char set of MC20
        f.close()
        g= open(f'.\\int_files\\font\\{name}lookup.txt',encoding='utf-8')         
        locals()[f'{name}lookup'] = g.read().split('\n')        #eg:if a font's name is MC20, this variable's name is MC20lookup,and it's the char's index of the char set of MC20
        g.close()

    f= open(dialog,encoding='utf-8')
    originals = f.read()            #originals is the dialog file
    f.close()
    
    trans =[]       #trans is the string of texts after chars' translation to tex's res
    default_font_name = default_font    #define default font,on which chars may fall back.
    marker1 =0      #$检测              #detect $ which marks the beginning of chars changing fonts, following by font's name
    counter =0      #*检测（字体套用范围）#detect *. First * marks the end of font's name and the beginning of the chars using the font,and the second * marks the end of chars using the font
    fontscan =''    #font name after $ 
    font_name =  default_font_name  #font_name is the final font the char is going to use,and may change.

    for item in originals :             #traverse through every char in the dialog file

        if item =='$':                  #字体更改开始，开始读取字体名称 #marks the beginning of change of font.
            marker1 =1                  #marker1 is the marker for $
            continue
        if item =='*' and counter ==0:      #字体名称结束，套用范围开始 #marks the end of the font's name and the beginning of chars going to use that font.
            marker1 =0                      #marker1 reset to 0
            counter =1                      #counter is the * detected,0 means no * has detected and 1 means 1 * already detected.
            font_name = fontscan            #font_name set to font get from between $ and *
            continue
        if item =='*' and counter ==1:      #套用范围结束   #marks the end of the chars going to use that font.
            counter =0                      #counter set to 0
            font_name = default_font_name   #font_name reset to default
            fontscan =''                    #scan sequence reset to null
            continue
        if marker1 ==1:                     #读取字体名称   #reads the font's name going to apply to chars.
            fontscan =fontscan+ item        #scan
            continue

        try:
            texts = locals()[f'{font_name}texts']           #if certain {font_name}texts cannot be found,all chars using that font will fall back to default font
        except KeyError:
            texts = locals()[f'{default_font_name}texts']
            fallback = 1

        try:                                                #if certain {font_name}lookup cannot be found,all chars using that font will fall back to default font
            name_lookup = locals()[f'{font_name}lookup'] 
        except KeyError:
            name_lookup = locals()[f'{default_font_name}lookup']
            fallback = 1
        

        if item in texts:   #if the char is found in its all_char.txt, append its res to translated texts.
            index= name_lookup[texts.index(item)]           #查询单字index  #search for char's unique name in lookup.txt
            if fallback == 0:                               
                trans.append('{'+f'animation={font_name}_{index}'+'}')              
            else:                                                                   #如未查到，fallback到默认字体   #fallback
                trans.append('{'+f'animation={default_font_name}_{index}'+'}')
                fallback =0
        else:               #if the char cannot be found in its all_char.txt:                                         
            if item not in locals()[f'{default_font_name}texts']:   #if it's not in default_font'range,just add.
                trans.append(item)                              #非汉字直接加入
            else:                                                   #if can be found in default_font'range, the char will fall back to default char and remind you.
                index= locals()[f'{default_font_name}lookup'][locals()[f'{default_font_name}texts'].index(item)]
                trans.append('{'+f'animation={default_font_name}_{index}'+'}')
                print(f'{item} fall back to {default_font_name}')
                
    if os.path.exists('.\\int_files') == False:
        os.makedirs('.\\int_files')
    f= open('.\\int_files\\english.txt','w',encoding='utf-8')             #输出编码后english.txt    #write to file.
    for tran in trans:  
        f.write(tran)
    f.close()

def check_fonts(file,font_file,default_font):      #输出各字体使用，默认字体不输出（因为所有字符都需要绘制，直接使用原文本即可）  
    f= open(file,encoding='utf-8')                               #check the usage and name of fonts used in dialog.It has some robustness which even if only
    chars= f.read()                                          #one char is used in one dialog line, it still covers all chars of tha dialog line in case you want to change.
    f.close()

    f= open(font_file,encoding='utf-8')             
    fonts_used= f.read().split('\n')
    f.close()
    for i in range(len(fonts_used)):
        reg = re.match('(.*?){.*',fonts_used[i])
        if reg!= None:
            font = reg.groups()[0]
        locals()[font]=[]
        fonts_used[i] = font
    '''
    pattern ='(#(?<=#).*?(?=#))'
    aa =re.findall(pattern,chars,re.S)
    for a in aa:
        for font in fonts_used:
            if font == default_font:
                continue
            if re.findall(font,a):
                locals()[font].append(a)
    '''
    for font in fonts_used:
        if font != default_font:
            pattern = f'(?<=\${font}\*)(.*?)(?=\*)'
            locals()[font].append(re.findall(pattern,chars,re.S))
        

    if os.path.exists('.\\int_files\\usage') == False:
        os.makedirs('.\\int_files\\usage')
    for font in fonts_used:
        if font == default_font:
            continue
        f= open(f'.\\int_files\\usage\\{font}usage.txt','w',encoding='utf-8') 
        for texts in locals()[font]:
            for item in texts:  
                f.write(str(item))
                f.write('\n')
        f.close()

def res_compile(tex_name):        #将各字体res组成完整贴图res   # combine all fonts' seperate res to one whole and add necessary pre-definition of the res.
    ds = os.listdir('.\\int_files\\res')
    i=0
    fonts_name =[]
    for d in ds:
        a = re.match(f'({tex_name}_.*?).res',d)
        if(a):
            fonts_name.append(a.groups()[0])
            i+= 1
    for name in fonts_name:
        f= open(f'.\\int_files\\res\\{name}.res',encoding='utf-8')         
        locals()[f'{name}_res'] = f.read()
        f.close()
    res =(f'Texture {tex_name}\n'
        '{\n'
        f'filename = Media/Tex/{tex_name}.png\n'
        f'resgroup = 0\n'
        '}\n'
        f"Animation credits_Xchiliarch\n"
        "{\n"
        f" texture = {tex_name}\n"
        f" rect = 0,4000,90,90\n"
        f" hotspot = 45,45\n"
        f" zorder = 0.000000\n"
        f" resgroup = 0\n"
        f" frame = 1\n"
        "}\n")
    for name in fonts_name:       
        res = res+ locals()[f'{name}_res']
    if os.path.exists('.\\build') == False:
        os.makedirs('.\\build')
    f= open(f'.\\build\\{tex_name}.res','w',encoding='utf-8')         
    f.write(res)
    f.close()

def font_params(fontfile,fontscan):     #输出字体参数   #return a font's parameter, in the order the order used in fonts.txt,default:coorX,coorY,rectX,rectY
    f= open(fontfile,encoding='utf-8')         
    fonts = f.read().split('\n')
    f.close()
    for item in fonts :
        a = re.match('(.*?){(.*?),(.*?),(.*?),(.*?)}',item)
        if a == None:
            continue
        if a.groups()[0] == fontscan:
            return a.groups()


