import pyaudio
import wave
from aip import AipSpeech
import wx
import serial

input_filename = "input.wav"               # 麦克风采集的语音输入
input_filepath = r""              # 输入文件的path
in_path = input_filepath + input_filename

""" 你的 APPID AK SK """
APP_ID = '17392569'
API_KEY = 'evonBLTfuMehYEpPadUGGsxL'
SECRET_KEY = 'aX8MLHdQgnB5sSfSFdX2B7LS25uO3dkR'

def send2serial(context):
    # 连接单片机
    ser = serial.Serial("COM3", 9600)
    try:
        # 查看状态
        if ser.isOpen():
            ser.write(bytes.fromhex(context))
        # 端口连接
    except serial.serialutil.SerialException:
        print("Error: 没有找到文件或读取文件失败")
        dlg = wx.MessageDialog(None, u"提醒", u"Error: 没有找到文件或读取文件失败", wx.OK | wx.ICON_QUESTION)
    else:
        print("内容写入文件成功")
        ser.close()

def get_audio(filepath, dic, language):
    print(in_path)
    CHUNK = 256
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # 声道数
    RATE = 11025  # 采样率
    RECORD_SECONDS = 8
    WAVE_OUTPUT_FILENAME = filepath
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    #print('开始录音：请在5秒内输入语音')
    text2.AppendText('开始录音：请在8秒内输入语音\n')
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        if i%43 == 0 :
            text2.AppendText(str(i//43 + 1) + '\n')
        data = stream.read(CHUNK)
        frames.append(data)

    #print('录音结束')
    text2.AppendText('录音结束\n')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    langcode = 1536

    if language == "普通话":
        langcode = 1536
    elif language == "粤语":
        langcode = 1637
    else:
        langcode = 1837

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    # 识别本地文件
    result = client.asr(get_file_content(in_path), 'wav', 16000, {'dev_pid': langcode, })

    # print(result)

    if result['err_msg'] == "success.":
        result = result['result'][0]
        #print("您说的是：" + result)
        classfy(result, dic)
    else:
        #print("您的表达不清楚!")
        text2.AppendText("您的表达不清楚!\n")

# 定义函数判断values属于哪个key
def get_key(value, dict):
    for k, v in list(dict.items()):
        if value in list(v):
            return k
    # 列表解析式
    return "无法得知该物品属于什么垃圾"

def readtxt():
    with open('data.txt', encoding="gbk") as file:
        # 上一行的参数！只使用'r'会出现报错：'gbk' codec can't decode byte 0xb7 in position 8: illegal multibyte sequence，输入encoding='utf-8'可解决
        # 只使用"utf-8"输出时会出现文件第一行多出十六进制编码，用'-sig'解决。
        data_line = file.readline()
        data_line = data_line.replace('\t', ',')
        data_line = data_line.strip('\n')
        keys = data_line.split(',')

        values_wet = set()  # set()是创建空集合的唯一方法
        values_dry = set()
        values_harm = set()
        values_re = set()

        while True:
            data_line = file.readline()
            if data_line != '':  # 解决最后一行问题，注意要加else: break，不然死循环
                data_line = data_line.strip('\n')
                data_line = data_line.replace('\t', ',')
                values = data_line.split(',')
                values_wet.add(values[1])  # 添加值到集合，".add()"方法
                values_dry.add(values[2])
                values_harm.add(values[3])
                values_re.add(values[4])
            else:
                break

    dic = {keys[1]: values_wet, keys[2]: values_dry, keys[3]: values_harm, keys[4]: values_re}

    wet_str = ""
    dry_str = ""
    harm_str = ""
    re_str = ""

    for i in values_wet:
        wet_str = wet_str + " " + i

    for i in values_dry:
        dry_str = dry_str + " " + i

    for i in values_harm:
        harm_str = harm_str + " " + i

    for i in values_re:
        re_str = re_str + i

    str_list = [wet_str, dry_str, harm_str, re_str]

    """vectorizer = CountVectorizer()  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf = transformer.fit_transform(vectorizer.fit_transform(str_list))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        print(u"-------这里输出第", i, u"类文本的词语tf-idf权重------")
        for j in range(len(word)):
            print(word[j], weight[i][j])

    cut_words = []

    for i in str_list:
        seg_list = jieba.cut(i, cut_all=False)
        cut_words.append(seg_list)
        #print("精准模式: " + "/ ".join(seg_list))  # 精确模式"""

    return dic, str_list

def classfy(result, dic):
    # 输出
    value1 = result
    #print("该物品属于：" + get_key(value1, dic))
    theclass = get_key(value1, dic)
    text2.AppendText("您说的是：" + value1 + "\n" + "该物品属于：" + theclass + "\n")
    if theclass == "湿垃圾":
        a = "aa"
        send2serial(a)
        print(a)
    elif theclass == "干垃圾":
        b = "bb"
        send2serial(b)
        print(b)
    elif theclass == "有害垃圾":
        c = "cc"
        send2serial(c)
        print(c)
    elif theclass == "可回收物":
        d = "dd"
        send2serial(d)
        print(d)
    else:
        print()

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def changeText(event):
    get_audio(in_path, dic, language)

def OnKeyDown(event):
    # 按键时相应代码
    kc = event.GetKeyCode()
    print(kc)
    if kc == 13:
        print(kc)
        get_audio(in_path, dic, language)

"""def on_combobox(event):
    print("选择{0}".format(event.GetString()))
    language = event.GetString()"""

app = wx.App()
dic, str_list  = readtxt()
language = ""
win = wx.Frame(None, title="语音识别垃圾分类小助手", size=(500, 500))
#win = KeyEvent(None, -1).win
button = wx.Button(win, label="开始录音", pos=(360, 10), size=(100, 30))
button.Bind(wx.EVT_BUTTON, changeText)
button.Bind(wx.EVT_KEY_DOWN, OnKeyDown)
# pos表示坐标，左上是0,0。 size表示宽高
text1 = wx.TextCtrl(win, pos=(5, 10), size=(250, 30), style=wx.TE_READONLY)  # 创建一个文本
#list=['普通话','粤语',"四川话"]
#ch1=wx.ComboBox(win, pos=(260, 10), size=(80, 100), value='普通话',choices=list,style=wx.CB_SORT)
#添加事件处理
#ch1.Bind(wx.EVT_COMBOBOX,on_combobox,ch1)
# 创建一个多行带滚动条的文本
text1.SetValue("是否开始录音？（按Enter键启动录音）")
text2 = wx.TextCtrl(win, pos=(0, 50), size=(480, 400), style=wx.TE_MULTILINE | wx.HSCROLL)
win.Show()
app.MainLoop()