# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

# 饼状图
labels = 'Frogs','Hogs','Dogs','Logs' #自定义标签
sizes = [15,30,45,10]   #每个标签占多大
explode = (0,0,0,0)  #将某部分爆炸出来

plt.pie(sizes,explode=explode,labels=labels,autopct='%1.1f%%',shadow=False,startangle=90)
    #autopct，圆里面的文本格式，%1.1f%%表示小数有1位，整数有一位的浮点数
    #shadow，饼是否有阴影
    #startangle，起始角度，0，表示从0开始逆时针转，为第一块。一般选择从90度开始比较好看
plt.axis('equal')   # 设置x，y轴刻度一致，这样饼图才能是圆的
plt.show()

# 直方图
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)   #每次生成的随即数都相同
mu , sigma = 100,20    #均值和标准差
a = np.random.normal(mu,sigma,size=100)    
#给出均值为mean，标准差为stdev的高斯随机数（场），当size赋值时，例如：size=100，表示返回100个高斯随机数。

plt.hist(a,10,histtype='stepfilled',facecolor='b',alpha=0.75)   #10是直方图的个数
plt.title('Histogram')  #标题
plt.show()

# 坐标图
import numpy as np
import matplotlib.pyplot as plt

N = 20
theta = np.linspace(0.0, 2 * np.pi, N , endpoint=False)
radii = 10 * np.random.rand(N)
width = np.pi / 4 * np.random.rand(N)

ax = plt.subplot(111,projection='polar')
bars = ax.bar(theta,radii,width=width,bottom=0.0)

for r,bar in zip(radii,bars):
    bar.set_facecolor(plt.cm.viridis(r / 10.))
    bar.set_alpha(0.5)
plt.show()

# 散点图
import numpy as np
import matplotlib.pyplot as plt

fig , ax = plt.subplots()
ax.plot(10*np.random.rand(100),10*np.random.rand(100),'o')
ax.set_title('Simple Scatter')

plt.show()

# 引力波
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

rate_h, hstrain = wavfile.read(r"H1_Strain.wav", "rb")
rate_l, lstrain = wavfile.read(r"L1_Strain.wav", "rb")
reftime, ref_H1 = np.genfromtxt('wf_template.txt').transpose()  # 使用python123.io下载文件

htime_interval = 1 / rate_h
ltime_interval = 1 / rate_l
fig = plt.figure(figsize=(12, 6))

# 丢失信号起始点
htime_len = hstrain.shape[0] / rate_h
htime = np.arange(-htime_len / 2, htime_len / 2, htime_interval)
plth = fig.add_subplot(221)
plth.plot(htime, hstrain, 'y')
plth.set_xlabel('Time (seconds)')
plth.set_ylabel('H1 Strain')
plth.set_title('H1 Strain')

ltime_len = lstrain.shape[0] / rate_l
ltime = np.arange(-ltime_len / 2, ltime_len / 2, ltime_interval)
pltl = fig.add_subplot(222)
pltl.plot(ltime, lstrain, 'g')
pltl.set_xlabel('Time (seconds)')
pltl.set_ylabel('L1 Strain')
pltl.set_title('L1 Strain')

pltref = fig.add_subplot(212)
pltref.plot(reftime, ref_H1)
pltref.set_xlabel('Time (seconds)')
pltref.set_ylabel('Template Strain')
pltref.set_title('Template')
fig.tight_layout()

plt.savefig("Gravitational_Waves_Original.png")
plt.show()
plt.close(fig)