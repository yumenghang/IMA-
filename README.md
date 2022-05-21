# 数据处理

## 数据文件

## Dict: physical_ports_information
键（key）：物理端口的全称，表示为：physical port full name。形式为：物理端口所属物理设备+"."+物理端口名，如物理设备IDURIGHTOUTBOARD上的A端口--IDURIGHTOUTBOARD.A，或物理端口所属机柜+"."+物理端口所属设备+"."+物理端口名，如机柜CCR_LEFT中物理设备GPM_L6上的A端口--CCR_LEFT.GPM_L6.A\
值（value）：为一列表，按以下格式存储对应物理端口的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;物理端口类型, #0\
&emsp;&emsp;&emsp;&emsp;物理端口标识符, #1\
&emsp;&emsp;&emsp;&emsp;physical port full name, #2\
&emsp;&emsp;&emsp;&emsp;NameDef, #3\
&emsp;&emsp;&emsp;&emsp;GuidDef, #4\
&emsp;&emsp;&emsp;&emsp;物理端口方向, #5 表示该物理端口是用于发送消息、接收消息还是同时发送与接收消息（注：ARINC-664与CAN协议的物理端口为双工，ARINC-429与Analog协议的物理端口为单工）\
&emsp;&emsp;&emsp;&emsp;该物理端口所在物理设备名称, #6\
&emsp;&emsp;]

### 二维数组: physical_ports_adjacent_matrix
记录物理端口（除电源接口外的所有物理端口）之间的连接关系\

### Dict: physical_ports_index
键（key）：物理端口的全称，physical port full name的名称，如：CCR_LEFT.GPM_L6.A，value为：该端口在邻接矩阵中的index\
值（value）：该物理端口在邻接矩阵physical_ports_adjacent_matrix中的index\

### Dict: physical_ports_index_reversed
键（key）：物理端口在邻接矩阵physical_ports_adjacent_matrix中的index\
值（value）：物理端口的全称，physical port full name的名称\

### Dict: switches_information
键（key）：交换机的标识符\
值（value）：为一列表，按以下格式存储对应交换机的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;交换机名称(注：一共有8台交换机，分别是：ARS_1A、ARS_2A、ARS_1B、ARS_2B、CCR_LEFT.ACS_LA、CCR_RIGHT.ACS_RA、CCR_LEFT.ACS_LB、CCR_RIGHT.ACS_RB), #0\
&emsp;&emsp;&emsp;&emsp;NameDef, #1\
&emsp;&emsp;&emsp;&emsp;GuidDef, #2\
&emsp;&emsp;&emsp;&emsp;[ 25*[ physical port full name ] ], #3\
&emsp;&emsp;]

### Dict: RDIU_information
键（key）：物理端口在邻接矩阵physical_ports_adjacent_matrix中的index\
值（value）：物理端口的全称，physical port full name的名称\

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
&emsp;&emsp;&emsp;&emsp;] #9\
&emsp;&emsp;]

#
#
