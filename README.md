# 数据处理
将原始数据中消息、物理端口及其连接关系等信息梳理清楚并存储。

## 原始数据文件
将原始数据文件（如：ATA 21 AMS、ATA 23 COM等）存放在Data Info文件夹下。\
Data Info与MAIN.py、FUNCTIONAL_CLASS.py文件存放于同一路径下

## 全局数据文件
统计全局数据（不区分A、B网）中的物理端口、消息、连接关系等的信息并存储

### Dict: physical_ports_information
键（key）：物理端口的全称，表示为：physical port full name。形式为：物理端口所属物理设备+"."+物理端口名，如物理设备IDURIGHTOUTBOARD上的A端口--IDURIGHTOUTBOARD.A，或物理端口所属机柜+"."+物理端口所属设备+"."+物理端口名，如机柜CCR_LEFT中物理设备GPM_L6上的A端口--CCR_LEFT.GPM_L6.A\
值（value）：为一列表，按以下格式存储对应物理端口的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;物理端口类型, #0，包括：AswPhysPort, AesPhysPort, CANPhysPort, AnalogPhysPort, A429PhysPort, PwrPhysPort\
&emsp;&emsp;&emsp;&emsp;物理端口标识符, #1\
&emsp;&emsp;&emsp;&emsp;physical port full name, #2\
&emsp;&emsp;&emsp;&emsp;NameDef, #3\
&emsp;&emsp;&emsp;&emsp;GuidDef, #4\
&emsp;&emsp;&emsp;&emsp;物理端口方向, #5 表示该物理端口是用于发送消息、接收消息还是同时发送与接收消息（注：ARINC-664与CAN协议的物理端口为双工，ARINC-429与Analog协议的物理端口为单工）\
&emsp;&emsp;&emsp;&emsp;该物理端口所在物理设备名称, #6\
&emsp;&emsp;&emsp;&emsp;该物理端口的传输速率（单位：MB/s）, #7\
&emsp;&emsp;]

### 二维数组: physical_ports_adjacent_matrix
记录物理端口（除电源接口外的所有物理端口）之间的连接关系

### Dict: physical_ports_index
键（key）：物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.A\
值（value）：该物理端口在邻接矩阵physical_ports_adjacent_matrix中的index

### Dict: physical_ports_index_reversed
键（key）：物理端口在邻接矩阵physical_ports_adjacent_matrix中的index\
值（value）：物理端口的全称，physical port full name

### Dict: switches_information
键（key）：交换机的标识符\
值（value）：为一列表，按以下格式存储对应交换机的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;交换机名称(注：一共有8台交换机，分别是：ARS_1A、ARS_2A、ARS_1B、ARS_2B、CCR_LEFT.ACS_LA、CCR_RIGHT.ACS_RA、CCR_LEFT.ACS_LB、CCR_RIGHT.ACS_RB), #0\
&emsp;&emsp;&emsp;&emsp;NameDef, #1\
&emsp;&emsp;&emsp;&emsp;GuidDef, #2\
&emsp;&emsp;&emsp;&emsp;[ physical port full name, ..., physical port full name  ], #3 （注：交换机内除电源接口外，共25个ARINC-664协议的物理端口）\
&emsp;&emsp;]

### Dict: RDIU_information
键（key）：RDIU名称(注：一共有16台交换机，分别是：RDIU_01、RDIU_02、RDIU_03、RDIU_04、RDIU_05、RDIU_06、RDIU_07、RDIU_08、RDIU_09、RDIU_10、RDIU_11、RDIU_12、RDIU_13、RDIU_14、RDIU_15、RDIU_16)\
值（value）：为一列表，按以下格式存储对应RDIU的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;RDIU名称, #0\
&emsp;&emsp;&emsp;&emsp;RDIU标识符, #1\
&emsp;&emsp;&emsp;&emsp;NameDef, #2\
&emsp;&emsp;&emsp;&emsp;GuidDef, #3\
&emsp;&emsp;&emsp;&emsp;[ physical port full name, ..., physical port full name ], #4\
&emsp;&emsp;]

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

messages_per_physical_port[physical_port_name] = [physical_port_name, message_type, message_size, message_latency, TransmissionIntervalMinimum, guid_of_messages, [ logical_destination_of_message ], [ physical_destination_of_message] ]

### Dict: messages_per_physical_port
键（key）：物理端口的全称，表示为：physical port full name。形式为：物理端口所属物理设备+"."+物理端口名，如物理设备IDURIGHTOUTBOARD上的A端口--IDURIGHTOUTBOARD.A，或物理端口所属机柜+"."+物理端口所属设备+"."+物理端口名，如机柜CCR_LEFT中物理设备GPM_L6上的A端口--CCR_LEFT.GPM_L6.A\
值（value）：为一列表，按以下格式存储对应物理端口的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;物理端口的全称, #0\
&emsp;&emsp;&emsp;&emsp;消息类型, #1，为一列表，包括：A664, CAN, A429, Analog\
&emsp;&emsp;&emsp;&emsp;消息大小, #2，为一列表，单位：Byte\
&emsp;&emsp;&emsp;&emsp;消息的系统延迟要求, #3，为一列表，单位：ms\
&emsp;&emsp;&emsp;&emsp;消息的发送周期, #4，为一列表，单位：ms\
&emsp;&emsp;&emsp;&emsp;消息的标识符, #5，为一列表\
&emsp;&emsp;&emsp;&emsp;消息的目的节点的逻辑端口, #6，因为同一消息可以被发送至多个目的节点，因此每一个消息的目的节点的逻辑端口是一个列表，因此此项是列表的列表，格式为：
[ [ logical_port_1, logical_port_2, ..., logical_port_m ], ... , [ logical_port_1, logical_port_2, ..., logical_port_n ] ]\
&emsp;&emsp;&emsp;&emsp;消息的目的节点的物理端口, #7，因为同一消息可以被发送至多个目的节点，而每一个目的节点的消息可能经由A、B两个端口同时转发，因此每一个消息的目的节点的物理端口是一个列表的列表，因此此项是列表的列表的列表，格式为：
[ [ [ physical_port_A, physical_port_B ], ... , [ physical_port_A, physical_port_B ] ], ..., [ [ physical_port_A ], ..., [ physical_port_B ] ] ]\
&emsp;&emsp;]

## A、B网中的数据文件
分别统计A、B网中的物理端口、消息、连接关系等的信息并存储

### 二维数组：arinc664_physical_ports_adjacent_matrix_for_A_NET
记录A网中ARINC-664协议物理端口之间的连接关系

### Dict: arinc664_physical_ports_index_for_A_NET
键（key）：A网中ARINC-664协议物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.A\
值（value）：该物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_A_NET中的index

### Dict: arinc664_physical_ports_index_reversed_for_A_NET
键（key）：A网中ARINC-664协议物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_A_NET中的index\
值（value）：物理端口的全称，physical port full name

### 二维数组：arinc664_physical_ports_adjacent_matrix_for_B_NET
记录B网中ARINC-664协议物理端口之间的连接关系

### Dict: arinc664_physical_ports_index_for_B_NET
键（key）：B网中ARINC-664协议物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.B\
值（value）：该物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_B_NET中的index

### Dict: arinc664_physical_ports_index_reversed_for_B_NET
键（key）：B网中ARINC-664协议物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_B_NET中的index\
值（value）：物理端口的全称，physical port full name
