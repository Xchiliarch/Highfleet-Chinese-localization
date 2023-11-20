'''
HF Chinese Localization
2023.11.20

Credits:
Huge thanks to stopnoanime for decrypting the dialog file of Highfleet , localization would never be possible without your work.
感谢 Homobanana,Iansniper,Commie-Spy,Rogo921,BI-XY,Xchiliarch,Eistin-Yite,OpaqueArc,KagaJiankui,Suesun-1132,xlmzg,LeberechtSchorner 参与汉化工作。
感谢所有参与提交汉化问题的群友。

'''
version = "2.2.0"

import re
from PIL import Image, ImageDraw, ImageFont
from json import load
import os
from math import ceil
from fontTools.ttLib.ttFont import TTFont
import argparse

default_font = 'SH20_SAND'               #确定默认字体
row_num = 51                        #贴图一行字符数 
tex_name = 'Static11'               #材质贴图名称   
font_file ='./fonts/fonts.json'              #字体名字       
translation_file = 'chinese_e.txt'    #汉化文件       
pic_file = "./pics/pics.json"

if os.path.exists('.\\build') == False:
    os.makedirs('.\\build')

parser = argparse.ArgumentParser(description=f'highfleet汉化项目 版本{version}')
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('-d','--debug',action="store_true", default=False,help="开启此参数后，\
                    贴图中中将以红色方块标识(若字体可绘制该方块)无法绘制的字符，供检查及补绘")
group1.add_argument('-f','--fallback',action="store_true", default=False,help="开启此参数后，\
                    贴图中将以红色默认字体(若字体可绘制该字符)绘制无法绘制的字符，供检查及补绘 ")
group1.add_argument('-ff','--forceFallback',action="store_true", default=False,help="开启此参数后，\
                    贴图中将以默认字体及目标颜色(若字体可绘制该字符)绘制无法绘制的字符 ⚠️该选项Fallback\
                    的字体可能并不会匹配于原网格上，请尽量手动绘制")
args = parser.parse_args()
debug = args.debug
fallback = args.fallback
forceFallback = args.forceFallback


#检测字符是否包含于字体中
def checkChar(ch,fontT):
    found = False
    table = fontT['cmap'].tables[0].ttFont.getBestCmap()
    if ord(ch) in table:
        found = True
    return found

#给出text等参数，绘制字符
def drawchar(draw,text,color,xy,font,default_font,fontT,fontSize,bleeding):
    rectX,rectY = fontSize
    x,y =xy
    tempx = x
    tempy = y - ceil(bleeding/(1000//rectY))
    canNotDraw = ''
    for i in range(len(text)):
        if checkChar(text[i],fontT):
            draw.text((tempx,tempy), text[i], font=font, fill=color)  
        else:
            canNotDraw += ' '+text[i]
            if(debug):
                draw.text((tempx,tempy), '■', font=font, fill="#ff0000") 
            elif(fallback):
                temppy = tempy - ceil((default_font[1].get("bleeding")-bleeding)/(1000//rectY))
                draw.text((tempx,temppy), text[i], font=default_font[0], fill="#ff0000") 
            elif(forceFallback):
                temppy = tempy - ceil((default_font[1].get("bleeding")-bleeding)/(1000//rectY))
                draw.text((tempx,temppy), text[i], font=default_font[0], fill=color) 
            else:
                draw.text((tempx,tempy), '', font=font, fill=color) 
        #若检测到该字体无法绘制则添加该字符至canNotDraw
        tempx = x if ((i+1)%row_num==0) else tempx + rectX #
        tempy = tempy + rectY  if ((i+1)%row_num==0) else tempy
    return canNotDraw

#检测字体获取对应信息绘制
def fontRenderer(fontsConfig,fontName,draw,text):
    config = fontsConfig[fontName]
    color =config["color"]
    font_path = f"./fonts/{config['font']}.ttf"  
    bleeding = config["bleeding"]
    fontSize = config["fontSize"]
    x =config["coorX"]
    y = config["coorY"]
    rectX = config["rectX"]
    rectY = config["rectY"]
    fontT = TTFont(font_path)
    if config.get("postFX") !=None:
        FX = config.get("postFX")   #[type,color,width(stroke)/dis(shadow)]
        if FX[0] == 'stroke':       #描边
            font = ImageFont.truetype(font_path, fontSize-FX[2]-2)
            defaultFont = [ImageFont.truetype(f"./fonts/{fontsConfig[default_font]['font']}.ttf", fontSize-FX[2]-2),fontsConfig[default_font]]
            x = x+FX[2]
            y = y+2*FX[2]
            drawchar(draw,text,FX[1],(x-FX[2],y),font,defaultFont,fontT,(rectX,rectY),bleeding)
            drawchar(draw,text,FX[1],(x+FX[2],y),font,defaultFont,fontT,(rectX,rectY),bleeding)
            drawchar(draw,text,FX[1],(x,y-FX[2]),font,defaultFont,fontT,(rectX,rectY),bleeding)
            drawchar(draw,text,FX[1],(x,y+FX[2]),font,defaultFont,fontT,(rectX,rectY),bleeding)
            return drawchar(draw,text,color,(x,y),font,defaultFont,fontT,(rectX,rectY),bleeding)
        if FX[0] == 'shadow': #投影
            defaultFont = [ImageFont.truetype(f"./fonts/{fontsConfig[default_font]['font']}.ttf", fontSize-FX[2]//2),fontsConfig[default_font]]
            font = ImageFont.truetype(font_path, fontSize-FX[2]//2)
            x = x+FX[2]//2
            y = y+FX[2]//4
            drawchar(draw,text,FX[1],(x-FX[2]/2,y+FX[2]/2),font,defaultFont,fontT,(rectX,rectY),bleeding)
            return drawchar(draw,text,color,(x,y),font,defaultFont,fontT,(rectX,rectY),bleeding)
        if FX[0] == 'pixel': #像素字体加粗  
            x += ceil(fontSize/10)
            y += ceil(fontSize/20)
            font = ImageFont.truetype(font_path, fontSize+1)
            defaultFont = [ImageFont.truetype(f"./fonts/{fontsConfig[default_font]['font']}.ttf", fontSize+1),fontsConfig[default_font]]
            drawchar(draw,text,color,(x-1,y-1),font,defaultFont,fontT,(rectX,rectY),bleeding)            
            font = ImageFont.truetype(font_path, fontSize)
            defaultFont = [ImageFont.truetype(f"./fonts/{fontsConfig[default_font]['font']}.ttf", fontSize),fontsConfig[default_font]]
            return drawchar(draw,text,color,(x,y),font,defaultFont,fontT,(rectX,rectY),bleeding)
    else:
        font = ImageFont.truetype(font_path, fontSize)
        defaultFont = [ImageFont.truetype(f"./fonts/{fontsConfig[default_font]['font']}.ttf", fontSize),fontsConfig[default_font]]
        return drawchar(draw,text,color,(x,y),font,defaultFont,fontT,(rectX,rectY),bleeding)

def replaceWithRes(text):
    res =''
    pattern = '\$(.*?)\*(.*?)\*'
    toReplace = re.match(pattern,text.group(0)) 
    font = toReplace.group(1)
    for char in toReplace.group(2):
        if (ord(char)>3000 or ord(char)==183):
            res += "{"
            res += f"animation={font}_{ord(char)}"
            res += "}"
        else:
            res += char
    #print(res)
    return res

def replaceWithDefault(text):
    res =''
    for char in text.group(0):
        if (ord(char)>3000 or ord(char)==183):
            res += "{"
            res += f"animation={default_font}_{ord(char)}"
            res += "}"
        else:
            res += char
    #print(res)
    return res

if __name__ == '__main__':

    f= open(translation_file,encoding='utf-8')  
    rawText =  f.read()     #打开文本
    f.close()

    f= open(font_file, 'r')    
    fontsConfig = load(f)   #读取字体参数
    f.close()

    f= open(pic_file, 'r')    
    picsConfig = load(f)   #读取额外贴图参数
    f.close()
    
    #1.生成#{fontName}Chars - 各字体使用字符如 SH65_SANDChars ==['料','燃']
    for item in fontsConfig:
        if item != default_font:
            globals()[f'{item}Text']=[]
            pattern = f'(?<=\${item}\*)(.*?)(?=\*)' #提取 $指定字体*字符* 中字符 
            globals()[f'{item}Text'] = (re.findall(pattern,rawText,re.S)) #
            
        else:
            globals()[f'{item}Text'] = rawText.splitlines() #{item}Text SH20_SANDText 

        globals()[f'{item}Chars'] = [] 
        for chars in globals()[f'{item}Text']:
            for char in chars:
                if (ord(char)>3000 or ord(char)==183)and (char not in globals()[f'{item}Chars']):
                    globals()[f'{item}Chars'].append(char)              #检测·及汉字区域字符
        globals()[f'{item}Chars'] = sorted(globals()[f'{item}Chars'])   #{item}Chars SH20_SANDChars
    print('获取字符信息完成\n')
    
    #2.生成字库图片
    width   = 4096
    height  = 4096
    image = Image.new("RGBA", (width, height), color=(255,0,0,0))  #RGBA
    draw = ImageDraw.Draw(image)
    draw.fontmode = 'L' #抗锯齿

    for fontName in fontsConfig:  
        text = globals()[f'{fontName}Chars']
        canNotDraw = fontRenderer(fontsConfig,fontName,draw,text)
        if canNotDraw !='':
            print(f"{fontName} \'{canNotDraw}\'绘制失败")
    #绘制字体

    for pic in picsConfig:
        coorX = picsConfig[pic].get("coorX")
        coorY = picsConfig[pic].get("coorY")
        image.paste(Image.open(f"./pics/{pic}.png"),(coorX,coorY))
    #绘制图片

    image.save(f".\\build\\{tex_name}.png")
    print('生成字库图完成\n')

    #3.生成字库对应res
    res =(f'Texture {tex_name}\n'
        '{\n'
        f'filename = Media/Tex/{tex_name}.png\n'
        f'resgroup = 0\n'
        '}\n')
    for fontName in fontsConfig:                                       
        FontRes = ''
        globals()[f'{fontName}Res'] = ''
        coorX = fontsConfig[fontName].get('coorX')                     #起始坐标X
        coorY = fontsConfig[fontName].get('coorY')                     #起始坐标Y
        rectX = fontsConfig[fontName].get('rectX')                     #字符宽度
        rectY = fontsConfig[fontName].get('rectY')                     #字符高度
        i = 0
        tempCoorX = coorX
        tempCoorY = coorY
        for char in globals()[f'{fontName}Chars']:
            FontRes = FontRes + (                                #the res of each char
                f"\nAnimation {fontName}_{ord(char)}\n"
                "{"
                f"\n texture = {tex_name}\n"
                f" rect = {tempCoorX},{tempCoorY},{rectX},{rectY}\n"
                f" hotspot = {rectX//2},{rectY//2}\n"
                f" zorder = 0.000000\n"
                f" resgroup = 0\n"
                f" frame = 1\n"
                "}\n"
            )  
            tempCoorX = coorX if ((i+1)%row_num==0) else tempCoorX + rectX
            tempCoorY = tempCoorY+ rectY  if ((i+1)%row_num==0) else tempCoorY
            i+=1
        globals()[f'{fontName}Res'] = FontRes
    #生成 字体res
    
    for pic in picsConfig:
        PicRes = ''
        coorX = picsConfig[pic].get('coorX')                    #起始坐标Y
        coorY = picsConfig[pic].get('coorY')                    #起始坐标Y
        rectX = picsConfig[pic].get('rectX')                    #图片宽度
        rectY = picsConfig[pic].get('rectY')                    #图片高度
        centerX = picsConfig[pic].get('centerX')                #X中心
        centerY = picsConfig[pic].get('centerY')                #Y中心
        PicRes += (f"\nAnimation {pic}\n"
            "{"
            f"\n texture = {tex_name}\n"
            f" rect = {coorX},{coorY},{rectX},{rectY}\n"
            f" hotspot = {centerX},{centerY}\n"
            f" zorder = 0.000000\n"
            f" resgroup = 0\n"
            f" frame = 1\n"
            "}\n")
        globals()[f'{pic}Res'] = PicRes
    #生成 图片res

    for pic in picsConfig:
        res += globals()[f'{pic}Res']
    for fontName in fontsConfig:
        res += globals()[f'{fontName}Res']
    #合并
    f= open(f'.\\build\\{tex_name}.res','w',encoding='utf-8')         
    f.write(res)
    f.close()
    print('生成字库res完成')

    #4.生成编码后文本
    splitText = rawText
    for fontName in fontsConfig:
        if fontName == default_font:
            continue
        pattern = f'(\${fontName}\*.*?\*)' 
        splitText = re.sub(pattern,replaceWithRes,splitText)    
    #对标记字体的汉字替换为res注册信息

    splitText = re.sub('.*?',replaceWithDefault,splitText)      
    #将剩余未标记汉字以default_font替换

    #5.生成enc文件
    chars = b''
    chars += splitText.encode("utf-8")
    b = 2531011
    f= open('.\\build\\english.seria_enc','wb')  
    for item in chars:
        if item ==13:   #ignore '\r'
            continue
        a = ((b ^ (b >> 15) ^ item) & 0xff)     #生成english.seria_enc 源代码来自https://github.com/stopnoanime/highfleet-dialog                
        f.write(a.to_bytes(1,byteorder='little', signed=False))
        b += 214013
    f.close()
    print('生成enc完成')