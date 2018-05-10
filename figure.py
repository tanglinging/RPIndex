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
from settings import FIG_PATH,DATA_PATH,TITLES,YLABELS,logger
import numpy
from matplotlib.axes import Axes

INTERVAL = 1
class DrawPic(object):

    def __init__(self,nrows = 1,ncols = 1 ,sharex = False, sharey = False):
        self.plt = plt
        self.fig , self.ax = self.plt.subplots(nrows=nrows,ncols=ncols,sharex=sharex,sharey=sharey)

    def _tight_layout_rotation(self):
        self.plt.xticks(rotation=90) #横坐标顺时针旋转45°
        self.plt.tight_layout()

    def _save_fig(self,path):
        self.plt.savefig(path)

    def _plt_cla(self):
        self.plt.cla() #清空上次绘制图形

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
        xList = []
        yList = []
        title = fileData[0]
        xlabel = title[0]
        legends = title[1:]
        for row in fileData[1:]:
            xList.append(datetime.strptime(row[0],"%Y%m%d%H%M%S"))
            yList.append([float(k) for k in row[1:-1] ])
        #数据转置
        yList = [ list(y) for y in zip(*yList)]
        return xList,yList,xlabel,legends

    def _draw_figure(self,xList,yList,legends, xlabel,ylabel,title="",ax = None):
        if ax is None:
            ax = self.ax
        for i in range(len(yList)):
            ax.plot_date(xList,yList[i],'-',label = legends[i])
        ax.xaxis.set_major_locator(mpl.dates.SecondLocator(interval =INTERVAL))
        majorFormatter = mpl.dates.DateFormatter("%Y%m%d%H%M%S")
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.autoscale_view()
        ax.set_xlabel = xlabel
        ax.set_ylabel = ylabel
        ax.set_titile = title
        ax.grid(True)
        ax.legend(loc = "best", frameon = False)

    def draw_figure_by_type(self,ntype):
        assert isinstance(self.ax, Axes)
        ntpye = ntype.lower()
        assert ntype in DATA_PATH.keys()
        assert ntype in FIG_PATH.keys()
        dpath = DATA_PATH['{0}'.format(ntype)]
        fpath = FIG_PATH['{0}'.format(ntype)]
        title = TITLES['{0}'.format(ntype)]
        ylabel = YLABELS['{0}'.format(ntype)]
        data = self._get_file_data(dpath)
        if not data:
            return
        xList,yList,xlabel,legends = self._pre_process_data(data)
        self._plt_cla()
        self._draw_figure(xList,yList,legends,xlabel,ylabel,title)
        self._tight_layout_rotation()
        self._save_fig(fpath)
    #############disk below:######################
    def _draw_disk_figure(self,xList,rw_counts,rw_bytes,rw_times):
        isinstance(self.ax,numpy.ndarray)
        xlabel = "time"
        #子图1画 read_counts、write_counts
        yList1,legends1 = zip(*[(v['data'],v['label']) for k,v in rw_counts.iteritems()])
        self._draw_figure(xList,yList1,legends1,xlabel,YLABELS['disk']['counts'],ax=self.ax[0])
        #子图2画 rbytes、wbytes
        yList2,legends2 = zip(*[(v['data'],v['label']) for k,v in rw_bytes.iteritems()])
        self._draw_figure(xList,yList2,legends2,xlabel,YLABELS['disk']['bytes'],ax=self.ax[1])
        #子图3画 rtime、wtime
        yList3,legends3 = zip(*[(v['data'],v['label']) for k,v in rw_times.iteritems()])
        self._draw_figure(xList,yList3,legends3,xlabel,YLABELS['disk']['times'],ax=self.ax[2])

        self._tight_layout_rotation()
        self._save_fig(FIG_PATH['disk'])

    def _get_disk_data(self,dpath):
        fileData = ""
        try:
            f = open(dpath,"r")
            fileData = f.read().split("\n")[:-1]
            f.close()
        except Exception, e:
            logger.exception("读取文件失败!")
            return None,None,None,None
        xlabel = 'time'
        #用语记录数据
        rw_counts = {}
        rw_bytes = {}
        rw_times = {}
        xList = []
        #用语记录数据所在的列
        rw_counts_index = []
        rw_bytes_index = []
        rw_times_index = []
        #动态获取各个列所在index
        data0 = fileData[0].split("\t")[:-1]
        for i in range(1,len(data0)):
            if data0[i] in ("read_counts","write_counts"):
                rw_counts_index.append(i)
                if i not in rw_counts:
                    rw_counts[i] = {}
                rw_counts[i]["label"] = data0[i]
                rw_counts[i]["data"] = []
            elif data0[i] in ("rbytes","wbytes"):
                rw_bytes_index.append(i)
                if i not in rw_bytes:
                    rw_bytes[i] = {}
                rw_bytes[i]['label'] = data0[i]
                rw_bytes[i]['data'] = []
            elif data0[i] in ("rtime","wtime"):
                rw_times_index.append(i)
                if i not in rw_times:
                    rw_times[i] = {}
                rw_times[i]['label'] = data0[i]
                rw_times[i]['data'] = []
        #动态获取各个列值
        for data in fileData[1:]:
            dd = data.split("\t")[:-1]
            xList.append(datetime.strptime(dd[0],"%Y%m%d%H%M%S"))
            for i in range(1,len(dd)):
                if i in rw_counts_index:
                    rw_counts[i]['data'].append(float(dd[i]))
                elif i in rw_bytes_index:
                    rw_bytes[i]['data'].append(float(dd[i]))
                elif i in rw_times_index:
                    rw_times[i]['data'].append(float(dd[i]))
        return xList,rw_counts,rw_bytes,rw_times

    def draw_disk_figure(self):
        '''
        因为disk的rbytes、rcount、rtime单位不同。
        需要单独画图
        3张子图：read_counts\write_counts、rbytes\wbytes、rtime\wtime
        '''
        params = self._get_disk_data(DATA_PATH['disk'])
        if params[0] is None:
            return
        try:
            self._draw_disk_figure(*params)
        except Exception,e:
            logger.exception("绘制disk图形失败！")

        self.plt.close()
if __name__ == "__main__":
    drawObj = DrawPic(nrows = 3, ncols = 1, sharex=True)
    drawObj.draw_disk_figure()
    drawObj = DrawPic(nrows = 1, ncols = 1)
    drawObj.draw_figure_by_type("cpu")
    drawObj.draw_figure_by_type("memory")
    drawObj.draw_figure_by_type("network")
