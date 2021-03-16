## mediapipe python

## 环境配置

- 安装mediapipe

```shell
#网速很快的话可以直接命令行安装
$pip install mediapipe

#网速慢试试国内源https://zhuanlan.zhihu.com/p/109939711
$pip install mediapipe -i https://pypi.tuna.tsinghua.edu.cn/simple

#发现使用whl安装速度也挺快，下载whl文件：https://pypi.org/project/mediapipe/#modal-close
$ pip install mediapipe-0.8.3.1-cp39-cp39-manylinux2014_x86_64.whl  

```

- 安装cv2

```shell
$pip install cv-py -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- 测试代码

```shell
#下载代码，里面自带测试视频或者使用摄像头
$git clone https://github.com/XiangLiHealthy/spider.git

#运行测试
$cd action_recongnition/ && python3 main.py
```

