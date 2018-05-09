#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: tanglingling
@contact: tanglingling@maimiaotech.com
@date: 2018-05-08 17:38
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from settings import FIG_PATH,DATA_PATH,TITLES,logger

class DrawPic(object):

    def __init__(self):
        self.plt = plt
        self.fig , self.ax = self.plt.subplots()

    def _set_axes(self,title):
        self.plt.xticks(rotation=45) #横坐标顺时针旋转45°
        #设置时间轴
        self.ax.xaxis.set_major_locator(mpl.dates.SecondLocator())
        majorFormatter = mpl.dates.DateFormatter("%Y%m%d%H%M%S")
        self.ax.xaxis.set_major_formatter(majorFormatter)
        self.ax.autoscale_view()
        #设置其他信息
        self.plt.xlabel = "time"
        self.plt.title = title
        self.plt.legend()
        self.plt.tight_layout()

    def _get_file_data(self,filePath):
        '''
        根据路径读取文件内容，并以list形式返回
        '''
        fileData = ""
        try:
            f = open(filePath,"r")
            fileData = f.read().split("\n")[:-1]
            f.close()
        except Exception, e:
            logger.error("读取文件失败!")
            return None
        lfileData = []
        for data in fileData:
            lfileData.append(data.split("\t"))
        return lfileData

    def _pre_process_data(self,fileData):
        '''
        传入list格式的fileData
        返回 legend 列表、横坐标、纵坐标list
        横坐标list肯定是 time
        '''
        xLabel = ""
        yLabels = []
        xList = []
        yList = []
        title = fileData[0]
        xLabel = title[0]
        yLabels = title[1:]
        for row in fileData[1:]:
            xList.append(datetime.strptime(row[0],"%Y%m%d%H%M%S"))
            yList.append([float(k) for k in row[1:-1] ])
        #数据转置
        yList = [ list(y) for y in zip(*yList)]
        return xList,yList,xLabel,yLabels

    def _draw_figure(self,xList,yList,xLabel,yLabels,savePath,title):
        self.plt.cla() #清空上次绘制图形
        for i in range(len(yList)):
            self.ax.plot_date(xList,yList[i],'-',label = yLabels[i])
        self._set_axes(title)
        self.plt.savefig(savePath)

    def draw_figure_by_type(self,ntype):
        ntpye = ntype.lower()
        assert ntype in DATA_PATH.keys()
        assert ntype in FIG_PATH.keys()
        dpath = DATA_PATH['{0}'.format(ntype)]
        fpath = FIG_PATH['{0}'.format(ntype)]
        title = TITLES['{0}'.format(ntype)]
        data = self._get_file_data(dpath)
        if not data:
            return
        xList,yList,xLabel,yLabels = self._pre_process_data(data)
        self._draw_figure(xList,yList,xLabel,yLabels,fpath,title)

if __name__ == "__main__":
    drawObj = DrawPic()
    drawObj.draw_figure_by_type("network")
