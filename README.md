# 数据处理

## 数据文件

## Dict: physical_ports_information

### 

### 

### Dict: messages_info
键（key）：消息（包括：ARINC-664消息、ARINC-429消息、CAN消息、Analog消息）的标识符\
值（value）：为一列表，按以下格式存储对应消息的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;发送端消息的类型, #0\
&emsp;&emsp;&emsp;&emsp;发送端消息的大小, #1\
&emsp;&emsp;&emsp;&emsp;发送端消息的名称, #2\
&emsp;&emsp;&emsp;&emsp;发送端消息所在的物理设备名称, #3\
&emsp;&emsp;&emsp;&emsp;发送端的物理端口名称, #4\
&emsp;&emsp;&emsp;&emsp;发送端的逻辑端口标识符, #5\
&emsp;&emsp;&emsp;&emsp;发送端逻辑端口名称, #6\
&emsp;&emsp;&emsp;&emsp;发送端的消息发送周期, #7\
&emsp;&emsp;&emsp;&emsp;[接收端逻辑端口名称], #8 这一项用于在消息合并过程中判断消息的接收端是否被重复加入\
&emsp;&emsp;&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[接收端消息的类型, 接收端消息的大小, 接收端对消息的延迟要求, 接收端所在的物理设备名称, 接收端的物理端口名称（注：这里为一列表，针对ARINC-664消息可能从同一物理设备的A、B两个端口进行接收，然后再传输至相应逻辑端口）, 接收端的逻辑端口标识符, 接收端的逻辑端口名称],\
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;... ...\
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[接收端消息的类型, 接收端消息的大小, 接收端对消息的延迟要求, 接收端所在的物理设备名称, 接收端的物理端口名称（注：这里为一列表，针对ARINC-664消息可能从同一物理设备的A、B两个端口进行接收，然后再传输至相应逻辑端口）, 接收端的逻辑端口标识符, 接收端的逻辑端口名称]\
&emsp;&emsp;&emsp;&emsp;], #9\
&emsp;&emsp;]\

#
#
