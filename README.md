# 数据处理
将原始数据中消息、物理端口及其连接关系等信息梳理清楚并存储。

## 原始数据文件
将原始数据文件（如：ATA 21 AMS、ATA 23 COM等）存放在Data Info文件夹下。\
Data Info与MAIN.py、FUNCTIONAL_CLASS.py文件存放于同一路径下

***

## 全局数据文件
统计全局数据（不区分A、B网）中的物理端口、消息、连接关系等的信息并存储

---

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

---

### 二维数组: physical_ports_adjacent_matrix
记录物理端口（除电源接口外的所有物理端口）之间的连接关系

---

### Dict: physical_ports_index
键（key）：物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.A\
值（value）：该物理端口在邻接矩阵physical_ports_adjacent_matrix中的index

### Dict: physical_ports_index_reversed
键（key）：物理端口在邻接矩阵physical_ports_adjacent_matrix中的index\
值（value）：物理端口的全称，physical port full name

---

### Dict: switches_information
键（key）：交换机的标识符\
值（value）：为一列表，按以下格式存储对应交换机的相关信息：\
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;交换机名称(注：一共有8台交换机，分别是：ARS_1A、ARS_2A、ARS_1B、ARS_2B、CCR_LEFT.ACS_LA、CCR_RIGHT.ACS_RA、CCR_LEFT.ACS_LB、CCR_RIGHT.ACS_RB), #0\
&emsp;&emsp;&emsp;&emsp;NameDef, #1\
&emsp;&emsp;&emsp;&emsp;GuidDef, #2\
&emsp;&emsp;&emsp;&emsp;[ physical port full name, ..., physical port full name  ], #3 （注：交换机内除电源接口外，共25个ARINC-664协议的物理端口）\
&emsp;&emsp;]

---

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

---

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

---

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

***

## A、B网中的数据文件
分别统计A、B网中的物理端口、消息、连接关系等的信息并存储

---

### 二维数组：arinc664_physical_ports_adjacent_matrix_for_A_NET
记录A网中ARINC-664协议物理端口之间的连接关系

---

### Dict: arinc664_physical_ports_index_for_A_NET
键（key）：A网中ARINC-664协议物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.A\
值（value）：该物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_A_NET中的index

---

### Dict: arinc664_physical_ports_index_reversed_for_A_NET
键（key）：A网中ARINC-664协议物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_A_NET中的index\
值（value）：物理端口的全称，physical port full name

---

### 二维数组：arinc664_physical_ports_adjacent_matrix_for_B_NET
记录B网中ARINC-664协议物理端口之间的连接关系

---

### Dict: arinc664_physical_ports_index_for_B_NET
键（key）：B网中ARINC-664协议物理端口的全称，physical port full name，如：CCR_LEFT.GPM_L6.B\
值（value）：该物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_B_NET中的index

---

### Dict: arinc664_physical_ports_index_reversed_for_B_NET
键（key）：B网中ARINC-664协议物理端口在邻接矩阵arinc664_physical_ports_adjacent_matrix_for_B_NET中的index\
值（value）：物理端口的全称，physical port full name

***
***

# 虚链路处理
将原始数据中的消息以物理设备及其端口为单位（如：RDIU_01.A, RDIU_01.B等），进行虚链路的划分。\
其中，以字典（Dict）：messages_per_physical_port为入手点。这里首先穷举以下messages_per_physical_port中的键值，也就是路由问题中虚链路的起点：
RDIU_01.A, RDIU_01.B, RDIU_02.A, RDIU_02.B, RDIU_03.A, RDIU_03.B, RDIU_04.A, RDIU_04.B, RDIU_05.A, RDIU_05.B,\
RDIU_06.A, RDIU_06.B, RDIU_07.A, RDIU_07.B, RDIU_08.A, RDIU_08.B, RDIU_09.A, RDIU_09.B, RDIU_10.A, RDIU_10.B,\
RDIU_11.A, RDIU_11.B, RDIU_12.A, RDIU_12.B, RDIU_13.A, RDIU_13.B, RDIU_14.A, RDIU_14.B, RDIU_15.A, RDIU_15.B,\
RDIU_16.A, RDIU_16.B,\
RDIU_01, RDIU_02, RDIU_03, RDIU_04, RDIU_05, RDIU_06, RDIU_07, RDIU_08,\
RDIU_09, RDIU_10, RDIU_11, RDIU_12, RDIU_13, RDIU_14, RDIU_15, RDIU_16,\
CCR_LEFT.GPM_L6.A, CCR_LEFT.GPM_L6.B, FCM_1.A, FCM_1.B, CCR_LEFT.GPM_L4.A, CCR_LEFT.GPM_L4.B, FADEC_L_CHA.A, FADEC_L_CHA.B,\
CCR_LEFT.GPM_L1.A, CCR_LEFT.GPM_L1.B, IDULEFTINBOARD.A, IDULEFTINBOARD.B, IDURIGHTINBOARD.A, IDURIGHTINBOARD.B,\
IDUCENTER.A, IDUCENTER.B, CCR_RIGHT.GPM_R1.A, CCR_RIGHT.GPM_R1.B, CCR_RIGHT.GPM_R5.A, 'CCR_RIGHT.GPM_R5.B,\
FADEC_R_CHA.A, FADEC_R_CHA.B, CCR_RIGHT.GPM_R3.A, CCR_RIGHT.GPM_R3.B, L_RPDU_A.A, L_RPDU_A.B, L_RPDU_B.A, L_RPDU_B.B,\
R_RPDU_A.A, R_RPDU_A.B, R_RPDU_B.A, R_RPDU_B.B, CCR_RIGHT.GPM_R6.A, CCR_RIGHT.GPM_R6.B, IDULEFTOUTBOARD.A, IDULEFTOUTBOARD.B,\
IDURIGHTOUTBOARD.A, IDURIGHTOUTBOARD.B, HARDWARE_AHMUINSTANCE.A, 'HARDWARE_AHMUINSTANCE.B, CCR_LEFT.GPM_L2.A, CCR_LEFT.GPM_L2.B,\
CCR_LEFT.GPM_L5.A, CCR_LEFT.GPM_L5.B, CCR_RIGHT.GPM_R4.A, CCR_RIGHT.GPM_R4.B, CCR_LEFT.GPM_L3.A, CCR_LEFT.GPM_L3.B,\
CCR_RIGHT.GPM_R2.A, CCR_RIGHT.GPM_R2.B, FCM_2.A, FCM_2.B, FCM_3.A, FCM_3.B, FADEC_L_CHB.A, FADEC_L_CHB.B,\
FADEC_R_CHB.A, FADEC_R_CHB.B, ISS_R.A, ISS_R.B, ISS_L.A, ISS_L.B, FWDEAFR.A, FWDEAFR.B, AFTEAFR.A, AFTEAFR.B,\
SYSTEST_PORT_LRU.A, SYSTEST_PORT_LRU.B, CCR_LEFT.ACS_LA.A, ARS_1B.B, ARS_2A.A, ARS_2B.B, CCR_LEFT.ACS_LB.B,\
ARS_1A.A, CCR_RIGHT.ACS_RA.A, CCR_RIGHT.ACS_RB.B\
其中键值不以".A"与".B"结尾的表示：需要经相应的RDIU设备合并、转换的非ARINC664消息。其余表示ARINC664消息，划分虚链路后，从相应的A端口或者B端口转发、路由。
建立两个字典：VL_DICT_OF_A_NET、VL_DICT_OF_B_NET，分别存储需要从A网、B网进行路由的虚拟链路，具体如下：
键（key）：设备+端口名（A或B），如：RDIU_01.A、RDIU_12.B、CCR_LEFT.GPM_L4.A、L_RPDU_A.B等
值（value）：为一列表，分别存储以下信息：
&emsp;&emsp;[\
&emsp;&emsp;&emsp;&emsp;[ BAG, MTU, BandWidth, [ [ message_guid of subVL0, ... ], [ message_guid of subVL1, ... ], [ message_guid of subVL2, ... ], [ message_guid of subVL3, ... ] ], [ [ logical_destination of subVL0, ... ], [ logical_destination of subVL1, ... ], [ logical_destination of subVL2, ... ], [ logical_destination of subVL3, ... ] ], [ [ physical_destination of subVL0 ], [ physical_destination of subVL1 ], [ physical_destination of subVL2 ], [ physical_destination of subVL3 ] ] ], #虚链路1\
&emsp;&emsp;&emsp;&emsp;[ BAG, MTU, BandWidth, [ message_guid, ..., message_guid ], [ logical_destination, ..., logical_destination ], [ physical_destination, ..., physical_destination ] ], #虚链路2\
&emsp;&emsp;&emsp;&emsp;..., #2\
&emsp;&emsp;&emsp;&emsp;[ BAG, MTU, BandWidth, [ [ message_guid of subVL0, ... ], [ message_guid of subVL1, ... ], [ message_guid of subVL2, ... ], [ message_guid of subVL3, ... ] ], [ [ logical_destination of subVL0, ... ], [ logical_destination of subVL1, ... ], [ logical_destination of subVL2, ... ], [ logical_destination of subVL3, ... ] ], [ [ physical_destination of subVL0 ], [ physical_destination of subVL1 ], [ physical_destination of subVL2 ], [ physical_destination of subVL3 ] ] ], #虚链路n\
&emsp;&emsp;]
注：从同一物理端口转发的虚链路可能有很多条，因此要分别记录其参数：BAG、MTU、BandWidth，以及该虚链路包含的消息（以列表的形式记录）、该虚链路的目的节点的逻辑端口（以列表的形式记录）、该虚链路的目的节点的物理端口（以列表的形式记录）

***

## 运行：
VL_CONFIGURATION.py, MESSAGES_PROCESSING.py, OPTIMIZATION_MODEL.py与MAIN.py, FUNCTIONAL_CLASS.py同目录\n
运行VL_CONFIGURATION.py即可： python VL_CONFIGURATION.py （注：VL_CONFIGURATION.py中有两个参数，GAP与TIMELIMITED，分别设置求解的预设精度与预设时间，默认均为None、1200s）\n
注意：\n
1、此版本以Gurobi作为优化器运行\n
2、VL_CONFIGURATION.py中定义了两个参数：GAP, TIMELIMITED = None, 600，分别用于设置求解精度以及求解时间上限。这里GAP定义为None，表示求解精度不做要求，TIMELIMITED设置为600s。TIMELIMITED有两个作用：a）在RDIU内，当因为消息数目过多，导致短时间内无法求出最优解时，TIMELIMITED为最终的求解时间上限；b）在End System内，因为消息数目过多，导致短时间内无法求出最优解时，TIMELIMITED是作为时间单位参与的。具体的求解时间上限是ARINC664消息数目除以10的余数再乘以TIMELIMITED，作为最终的求解时间上限。举例：当消息数目为78时，求解时间上限是：int(78/10)$\times$TIMELIMITED = 4200（s）。
因此，运行一遍程序耗时较长。如果不能接受，可以适当调小TIMELIMITED的数值，但不可过小，防止终端内优化问题无法求出解（终端内优化问题参数较多，约束较多，因此耗时较长）。

***

## RDIU设备内虚链路的处理
首先将RDIU内需要合并、转发的非ARINC664消息，以CAN、ARINC429、Analog的消息格式进行划分，然后再分别以目的节点为A端口或者B端口进行划分（注:当目的节点为ARINC664协议的物理端口时，因为已经注明A端口或者B端口，因此，根据注明的信息进行区分即可；当目的节点是以非ARINC664的格式接收消息时，也就是说虚链路需要先经RDIU的转换、拆分，然后再转发至相应设备上的非ARINC664物理端口，我们默认虚链路仅从A网进行转发）


***

## End System内虚链路的处理 
首先将终端（End System）内需要转发的ARINC664消息，分别以目的节点为A端口或者B端口进行划分
