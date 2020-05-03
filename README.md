# LinkMapParse
解析linkmap文件，输出各模块占用大小，有考虑__bss段的剔除.

## 依赖prettytable
pip install prettytable 如果失败，可尝试 sudo pip install prettytable

## 使用方式
1. 拷贝linkmap文件到同级目录
2. 执行 python linkMap.py
3. 分析完成后，在同级目录下输出 parseResult.txt

![image](https://github.com/zc09v/LinkMapParse/blob/master/readMeImg/result.png)
