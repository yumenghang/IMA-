from xml.dom.minidom import parse
import numpy as np
import os

class GET_INFO:
    def __init__(self, root_path):
        self.root_path = root_path
        self.get_xml_path = GET_XML_PATH(self.root_path)

    def get_hardware_info(self):
        # 获取所有分系统下硬件设备的相对路径，[ root_path/***/Hardware/Instances/**.xml, ..., root_path/***/Hardware/Instances/**.xml ]
        xml_files_of_hardware = self.get_xml_path.get_xml_path_of_hardware()

        physical_ports_information, switches_information, RDIU_information = dict(), dict(), dict()
        for xml_file in xml_files_of_hardware:
            parse_xml = PARSE_XML(xml_file)
            physical_ports_information, switches_information, RDIU_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix = parse_xml.parse_hardware(
                physical_ports_information, switches_information, RDIU_information)
        return physical_ports_information, switches_information, RDIU_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix

    def get_hosted_applications_and_hosted_functions_info(self):
        #获取所有分系统下:
        #驻留应用（Hosted Applications）的相对路径，[ root_path/***/Hosted Applications/Instances/**.xml, ..., root_path/***/Hosted Applications/Instances/**.xml ]
        #驻留应用（Hosted Functions）的相对路径，[ root_path/***/Hosted Applications/Instances/**.xml, ..., root_path/***/Hosted Functions/Instances/**.xml ]
        xml_files_of_hosted_applications_and_hosted_functions = self.get_xml_path.get_xml_path_of_hosted_applications_and_hosted_functions()

        """
        遍历所有驻留应用（**.xml），返回相关信息。难点：
        1, 每个驻留应用（Hosted Applications或者Hosted Functions）包含数目不定的逻辑端口（Logical Port），用于消息的收或发；
        2, 如果逻辑端口用于发送消息，那么此端口有且仅有一条消息发送；如果逻辑端口用于接收消息，那么此端口通常情况下，也只用于接收一条消息，但也有同时接收来自不同逻辑发送端口的多条消息的情况存在；
        3, 发送端的逻辑端口，不会注明消息的目的地，包括逻辑接收端口、接收驻留应用以及接收物理设备；
        4, 接收端的逻辑端口，会注明消息的来源
        因此如果要将消息的发送端口与接收端口联系起来，需要：
        1, 建立字典messages_tx，键值（key）为消息的标识符，值（value）为一列表，存储以下属性值：
            [ 消息类型（A664Message, CANMessage, A429Message, AnalogDiscreteParameter）, 消息名, 驻留物理设备, 逻辑端口标识符, 逻辑端口名 ]
        2, 建立字典messages_rx，键值（key）为接收消息的Pub_Ref的标识符，值（value）为一列表，存储以下属性值：
            [ 逻辑端口标识符, 逻辑端口名 ]
        3, 因为发送消息的DP与接收消息的Pub_Ref是一一对应的，因此需要建立一个用于反向查询的字典ref_table,键值（key）为DP的标识符，值（value）为一列表，存储以下属性值：
            [ 消息的标识符, 消息名, 逻辑端口标识符, 逻辑端口名 ]
            因此根据接收端消息的Pub_Ref的标识符，通过ref_table的查询，可以查询到此消息的发送相关属性，包括：消息的标识符, 消息名, 逻辑端口标识符, 逻辑端口名
            至此，消息的发送端与接收端建立起联系
        4, 因为实际上，消息的发送端口与消息的接收端口是一对多的映射关系，因此，在存储消息的发、收关系时，决定建立如下的数据结构：
            messages_info = dict()
            messages_info[ message.Guid ] = [ 消息类型（A664Message, CANMessage, A429Message, AnalogDiscreteParameter）, 消息名, 发送端驻留物理设备, 发送端逻辑端口标识符, 发送端逻辑端口名, set( 接收端逻辑端口标识符 ) ] 
        """
        messages_tx, messages_rx, ref_table = dict(), dict(), dict()
        for xml_file in xml_files_of_hosted_applications_and_hosted_functions:
            parse_xml = PARSE_XML(xml_file)
            messages_tx, messages_rx, ref_table = parse_xml.parse_hosted_applications_and_hosted_functions(messages_tx, messages_rx, ref_table)
        return messages_tx, messages_rx, ref_table

class GET_XML_PATH:
    # 获取目标xml文件的相对路径
    def __init__(self, root_path):
        self.root_path = root_path

        # 获取路径root path下所有分系统
        self.sub_systems = []
        for sub_file in os.listdir(self.root_path):
            self.sub_systems.append(sub_file)

    # 获取所有分系统下硬件设备的相对路径，[ root_path/***/Hardware/Instances/**.xml, ..., root_path/***/Hardware/Instances/**.xml ]
    def get_xml_path_of_hardware(self):
        xml_files = []
        for sub_system in self.sub_systems:
            if os.path.exists(self.root_path + sub_system + "/Hardware/Instances/"):
                for xml_file in os.listdir(self.root_path + sub_system + "/Hardware/Instances/"):
                    xml_files.append(self.root_path + sub_system + "/Hardware/Instances/" + xml_file)
        return xml_files

    # 获取所有分系统下分区(Hosted Applications与Hosted Functions)的相对路径
    # [ root_path/***/Hosted Applications/Instances/**.xml, ..., root_path/***/Hosted Applications/Instances/**.xml ]
    # [ root_path/***/Hosted Functions/Instances/**.xml, ..., root_path/***/Hosted Functions/Instances/**.xml ]
    def get_xml_path_of_hosted_applications_and_hosted_functions(self):
        xml_files = []
        for sub_system in self.sub_systems:
            if os.path.exists(self.root_path + sub_system + "/Hosted Applications/Instances/"):
                for xml_file in os.listdir(self.root_path + sub_system + "/Hosted Applications/Instances/"):
                    xml_files.append(self.root_path + sub_system + "/Hosted Applications/Instances/" + xml_file)

        for sub_system in self.sub_systems:
            if os.path.exists(self.root_path + sub_system + "/Hosted Functions/Instances/"):
                for xml_file in os.listdir(self.root_path + sub_system + "/Hosted Functions/Instances/"):
                    xml_files.append(self.root_path + sub_system + "/Hosted Functions/Instances/" + xml_file)

        return xml_files

    # 获取所有分系统下Logical Busses文件的相对路径
    # [ root_path/***/Logical Busses/**.xml, ..., root_path/***/Logical Busses/**.xml ]
    def get_xml_path_pf_logical_busses(self):
        xml_files = []
        for sub_system in self.sub_systems:
            if os.path.exists(self.root_path + sub_system + "/Logical Busses/"):
                for xml_file in os.listdir(self.root_path + sub_system + "/Logical Busses/"):
                    xml_files.append(self.root_path + sub_system + "/Logical Busses/" + xml_file)

        # 因为"Data Info/ATA 42 IMA/Hardware/Instances/CCR_LEFT"与"Data Info/ATA 42 IMA/Hardware/Instances/CCR_RIGHT"两个文件中也有物理端口的连接关系
        # 因此xml_files也要添加这两个路径

        xml_files.append("Data Info/ATA 42 IMA/Hardware/Instances/CCR_LEFT.xml")
        xml_files.append("Data Info/ATA 42 IMA/Hardware/Instances/CCR_RIGHT.xml")
        return xml_files

class PARSE_XML:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.DOMTree = parse(self.xml_file)
        self.root_node = self.DOMTree.documentElement

    """
    统计所有物理设备上物理端口的信息
    物理端口种类：AswPhysPort, AesPhysPort, CANPhysPort, AnalogPhysPort, A429PhysPort, PwrPhysPort
    物理设备xml文件根节点的标签："LRU", "RIU", "ARS", "ACS", "CCR", "GPM"
    LRU: 一般的终端设备
    RIU: RDIU设备
    ARS, ACS: 交换机. 区别在于：前者为远端交换机，后者为近端交换机
    CCR: 严格意义上来讲并不是物理设备，它是一个机柜，包含上述的一些物理设备，如：LRU、RIU、ARS、ACS以及GPM
    GPM: 一个包含且仅包含两个ARINC664端口的物理设备

    层级关系：
    物理端口标签被包含在物理设备的标签中："LRU", "RIU", "ARS", "ACS", "GPM"
    机柜"CCR"的子标签为上述其它物理设备以及一些内部连接关系标签（<LB>...</LB>），而不直接是物理端口的标签
    所以，不同物理设备标签的xml文件的结构并不相同，下面给出示例：
    1, LRU:
        <LRU ...>
            <PwrPhysPort ... />
            <PwrPhysPort ... />
            <CANPhysPort ... />
            <CANPhysPort ... />
            <AnalogPhysPort ... />
        </LRU>
        即: 根节点的子节点即为该物理设备的物理端口，包括数目不定的物理端口（AesPhysPort, CANPhysPort, AnalogPhysPort, A429PhysPort, PwrPhysPort）

    2, RIU
        <RIU Name="RDIU_01" ...>
            <AnalogPhysPort Name="40022_A02"... />
            <AesPhysPort Name="A" ... />
            <AesPhysPort Name="B" ... />
            <CANPhysPort Name="40009_A01" ... />
            ...
            <AnalogPhysPort Name="40022_B05" ... />
            <A429PhysPort Name="40006_A03" ... />
            <AnalogPhysPort Name="40012_B01" de Output,DOP_GND_SBY_OUTPUT_1;" TemplateInstance="40012_B01" />
            <PwrPhysPort Name="Pwr_1" ... />
        </RIU>
        即：根节点的子节点即为该物理设备的物理端口，包括数目不定的物理端口（CANPhysPort, AnalogPhysPort, A429PhysPort, PwrPhysPort）以及2个（数目固定）ARINC664端口（AesPhysPort）

    3, ARS
        <ARS Name="ARS_1A" ...>
            <AswPhysPort Name="A664_PORT_01" ... />
            <AswPhysPort Name="A664_PORT_02" ... />
            <AswPhysPort Name="A664_PORT_03" ..." />
            <AswPhysPort Name="A664_PORT_04" ... />
            ...
            <AswPhysPort Name="A664_PORT_24" ... />
            <PwrPhysPort Name="Pwr_1" ... />
            <PwrPhysPort Name="Pwr_2" ... />
        </ARS>
        即：根节点的子节点即为该物理设备的物理端口，包括24个对外的（数目固定）ARINC664物理端口（AswPhysPort），1个对内的ARINC664物理端口（AswPhysPort，根据该交换机所在是A网还是B网，定义其物理端口名为'A'或'B'）以及其它物理端口（如：PwrPhysPort）

    4, Tag: ACS
        <ACS Name="ACS_LA" ...>
            <AswPhysPort Name="A664_PORT_01" ... />
            <AswPhysPort Name="A664_PORT_02" ... />
            <AswPhysPort Name="A664_PORT_03" ..." />
            <AswPhysPort Name="A664_PORT_04" ... />
            ...
            <AswPhysPort Name="A664_PORT_24" ... />
            <PwrPhysPort Name="Pwr_1" ... />
            <PwrPhysPort Name="Pwr_2" ... />
        </ACS>
        即：根节点的子节点即为该物理设备的物理端口，包括24个对外的（数目固定）ARINC664物理端口（AswPhysPort），1个对内的ARINC664物理端口（AswPhysPort，根据该交换机所在是A网还是B网，定义其物理端口名为"A"或"B"）以及其它物理端口（如：PwrPhysPort）

    5, Tag: GPM
        <GPM Name="GPM_L1" ...>
            <AesPhysPort Name="A" ... />
            <AesPhysPort Name="B" ... />
            <GPMSchedule Name="Schedule1" ScheduleID="1" MajorTimeFrame="500">
                <ScheduleWindow Name="APP_FMS_DATALINK_1" WindowDuration="8" />
                ...
                <ScheduleWindow Name="SPARE" WindowDuration="29.5" />
            </GPMSchedule>
            ...
            <GPMSchedule Name="Schedule1" ScheduleID="1" MajorTimeFrame="500">
                <ScheduleWindow Name="APP_FMS_DATALINK_1" WindowDuration="8" />
                ...
                <ScheduleWindow Name="SPARE" WindowDuration="29.5" />
            </GPMSchedule>
        </GPM>
        即：仅有前两个子标签为ARINC664端口

    6, CCR
        <CCR Name="CCR_LEFT" Guid="aBBB073C3-6657-4f4a-B25A-60BDE8398F69a" XsdVersion="8.8" ATA="422100" DCPowerBudgeted="130" GEResponsible="True" MTBFBudgeted="145501" ThermalCoolingMethod="Forced Convection" VolumeBudgeted="108425.142" WeightBudgeted="11.5">
            <ACS Name="ACS_LA" Guid="a2A130988-96C7-44ee-9D96-6EEC5885B27Ea" NameDef="ACS_LA_Class" GuidDef="a27BB3EE2-F3DA-492e-8DD2-80D6597D0BA0a" EquipmentPosition="34" MACAddress="2.0.0.2A.22.20">
                <AswPhysPort Name="A664_PORT_01" Guid="a20106102-9349-404e-8168-18D020591C31a" NameDef="ACS_LA_Class.A664_PORT_01" GuidDef="a697D031C-518B-4e36-9941-D31D0B896881a" CalculatedWatermark="13;27" PriorityQueueDepth="466;558" />
                    ...
                <AswPhysPort Name="A664_PORT_24" Guid="a307B70B3-2E5C-4f2b-8DAF-84AF891DAD01a" NameDef="ACS_LA_Class.A664_PORT_24" GuidDef="a80F22ECA-9ABE-4e45-A248-7D4C71F507A5a" CalculatedWatermark="10;35" PriorityQueueDepth="432;592" />
            </ACS>
            ...
            <ACS Name="ACS_LB" Guid="a414A1477-7EF6-4f39-97A1-58E33252A420a" NameDef="ACS_LB_Class" GuidDef="a0bb3b6ad-ddf8-4144-9847-7b6db363dc48a" EquipmentPosition="36" MACAddress="2.0.0.2A.24.40">
                <AswPhysPort Name="A664_PORT_01" Guid="a8C2BBD79-666F-4ca4-92C9-23B4F078998Aa" NameDef="ACS_LB_Class.A664_PORT_01" GuidDef="a6d5d92fd-7972-4c60-8476-8639906fac5fa" CalculatedWatermark="13;27" PriorityQueueDepth="467;557" />
                    ...
                <AswPhysPort Name="A664_PORT_24" Guid="a510F3011-E372-4977-9C10-8C2123CCD744a" NameDef="ACS_LB_Class.A664_PORT_24" GuidDef="a5ae3e8fe-2ed8-4121-8a7e-2b6990cd2f3da" CalculatedWatermark="12;42" PriorityQueueDepth="406;618" />
            </ACS>
            <LB Name="GPM_L1_A664_A" Guid="a89E05C06-6129-4893-844C-F7E6EC859CD5a" PhysProtocolType="A664">
                <Port_Ref Name="CCR_LEFT.ACS_LA.A664_PORT_01" Guid="a20106102-9349-404e-8168-18D020591C31a" />
                <Port_Ref Name="CCR_LEFT.GPM_L1.A" Guid="aDC78B1AB-4512-46e4-A467-76759DF88BBCa" />
            </LB>
            ...
            <LB Name="GPM_L6_A664_B" Guid="aBE05D67C-AD56-44d8-BFE1-7C1A7AE28271a" PhysProtocolType="A664">
                <Port_Ref Name="CCR_LEFT.ACS_LB.A664_PORT_06" Guid="aB83B8C08-F50B-4992-ACE1-262660A13B11a" />
                <Port_Ref Name="CCR_LEFT.GPM_L6.B" Guid="a5BFFE85A-61A1-466a-96A4-4C781A6FC1A2a" />
            </LB>
            <GPM Name="GPM_L1" Guid="a95FCF5B9-1D11-4800-A68C-640D1C86BEEFa" NameDef="GPMClass" GuidDef="aEC54B9B2-47F4-4123-83C6-7A85E5F22A07a" EdeSubscriberIndex="1" EquipmentPosition="40" HwTableBankIndex="1">
                ...
            </GPM>
            ...
            <GPM Name="GPM_L5" Guid="a80E14ED5-A712-4661-B3FA-647E729D7D72a" NameDef="GPMClass" GuidDef="aEC54B9B2-47F4-4123-83C6-7A85E5F22A07a" EdeSubscriberIndex="5" EquipmentPosition="44" HwTableBankIndex="1">
                ...
            </GPM>
        </CCR>
        即：CCR作为机柜，根节点的子节点为ACS、GPM等物理设备或LB等物理连接关系，物理端口信息标签在ACS、GPM等物理设备标签内

    因此，统计所有设备的物理端口信息，需要针对上述各种情况，分别考虑

    physical_ports_index: 字典，键值为physical port full name，格式为: 设备+"."+物理端口名(如: IDURIGHTOUTBOARD.A)，或者: 机柜+"."+设备+"."+物理端口名(如: CCR_LEFT.GPM_L6.A)，value为: [物理端口类型, 物理端口标识符, physical port full name, NameDef, GuidDef, 物理端口方向, 该物理端口所在物理设备名称]
        注意：physical port full name与物理端口名不同，前者描述得更详细
    switches_information: 字典，键值为交换机的Guid，value为: [ 交换机名称(如：ARS_1A, CCR_LEFT.ACS_LA), NameDef, GuidDef, [ 25*[ physical port full name ] ] ]
    """

    def parse_hardware(self, physical_ports_information, switches_information, RDIU_information):
        hard_ware = self.root_node.getAttribute("Name")  # 物理端口所在物理设备名称
        if self.root_node.nodeName == "LRU":  # 物理设备为一般终端设备
            class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + self.root_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
            get_direction = GET_DIRECTION(class_xml_file)
            physical_ports_direction = get_direction.get_direction()
            phys_port_nodes = self.root_node.childNodes  # 根节点的子节点列表，包括所有物理端口标签
            for phys_port_node in phys_port_nodes:
                if phys_port_node.nodeName != "#text":
                    physical_ports_information[hard_ware + "." + phys_port_node.getAttribute("Name")] = [
                        phys_port_node.nodeName,  # 物理端口类型
                        phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                        hard_ware + "." + phys_port_node.getAttribute("Name"),  # physical port full name
                        phys_port_node.getAttribute("NameDef"),
                        phys_port_node.getAttribute("GuidDef"),
                        physical_ports_direction[phys_port_node.getAttribute("GuidDef")],  # 物理端口方向
                        self.root_node.getAttribute("Name")  # 物理设备名称
                        ]
        elif self.root_node.nodeName == "RIU":  # 物理设备为RDIU
            class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + self.root_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
            get_direction = GET_DIRECTION(class_xml_file)
            physical_ports_direction = get_direction.get_direction()
            phys_port_nodes = self.root_node.childNodes
            phys_port_list = []
            for phys_port_node in phys_port_nodes:
                if phys_port_node.nodeName != "#text":
                    physical_ports_information[hard_ware + "." + phys_port_node.getAttribute("Name")] = [
                        phys_port_node.nodeName,  # 物理端口类型
                        phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                        hard_ware + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                        phys_port_node.getAttribute("NameDef"),
                        phys_port_node.getAttribute("GuidDef"),
                        physical_ports_direction[phys_port_node.getAttribute("GuidDef")],  # 物理端口方向
                        self.root_node.getAttribute("Name")  # 物理设备名称
                        ]
                    if phys_port_node.nodeName != "PwrPhysPort":  # 电源接口不必统计在RDIU信息哈希表中
                        phys_port_list.append(hard_ware + "." + phys_port_node.getAttribute("Name"))
            RDIU_information[hard_ware] = [
                hard_ware,
                self.root_node.getAttribute("Guid"),
                self.root_node.getAttribute("NameDef"),
                self.root_node.getAttribute("GuidDef"),
                phys_port_list
            ]
        elif self.root_node.nodeName == "ARS":  # 物理设备为远端交换机
            class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + self.root_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
            get_direction = GET_DIRECTION(class_xml_file)
            physical_ports_direction = get_direction.get_direction()
            phys_port_nodes = self.root_node.childNodes
            phys_port_list = []
            if self.root_node.getAttribute("Network") == "A":
                phys_port_list.append(hard_ware + ".A")  # 交换机有一个.A的物理端口
                physical_ports_information[hard_ware + ".A"] = [
                    "AswPhysPort",  # 物理端口类型
                    None,  # 物理端口标识符
                    hard_ware + ".A",  # physical port full name
                    None,
                    None,
                    "Bidirection",  # 物理端口方向
                    hard_ware  # 物理设备名称
                ]
            if self.root_node.getAttribute("Network") == "B":
                phys_port_list.append(hard_ware + ".B")  # 交换机有一个.B的物理端口
                physical_ports_information[hard_ware + ".B"] = [
                    "AswPhysPort",  # 物理端口类型
                    None,  # 物理端口标识符
                    hard_ware + ".B",  # 物理端口名称
                    None,
                    None,
                    "Bidirection",  # 物理端口方向
                    hard_ware  # 物理设备名称
                ]
            for phys_port_node in phys_port_nodes:
                if phys_port_node.nodeName != "#text":
                    physical_ports_information[hard_ware + "." + phys_port_node.getAttribute("Name")] = [
                        phys_port_node.nodeName,  # 物理端口类型
                        phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                        hard_ware + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                        phys_port_node.getAttribute("NameDef"),
                        phys_port_node.getAttribute("GuidDef"),
                        physical_ports_direction[phys_port_node.getAttribute("GuidDef")],  # 物理端口方向
                        hard_ware  # 物理设备名称
                        ]
                    if phys_port_node.nodeName != "PwrPhysPort":  # 电源接口不必统计在交换机信息哈希表中
                        phys_port_list.append(hard_ware + "." + phys_port_node.getAttribute("Name"))
            switches_information[self.root_node.getAttribute("Guid")] = [
                hard_ware,
                self.root_node.getAttribute("NameDef"),
                self.root_node.getAttribute("GuidDef"),
                phys_port_list
            ]
        elif self.root_node.nodeName == "ACS":  # 物理设备为近端交换机
            class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + self.root_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
            get_direction = GET_DIRECTION(class_xml_file)
            physical_ports_direction = get_direction.get_direction()
            phys_port_nodes = self.root_node.childNodes
            phys_port_list = []
            if self.root_node.getAttribute("Network") == "A":
                phys_port_list.append(hard_ware + ".A")  # 交换机有一个.A的物理端口
                physical_ports_information[hard_ware + ".A"] = [
                    "AswPhysPort",  # 物理端口类型
                    None,  # 物理端口标识符
                    hard_ware + ".A",  # 物理端口名称
                    None,
                    None,
                    "Bidirection",  # 物理端口方向
                    hard_ware  # 物理设备名称
                ]
            if self.root_node.getAttribute("Network") == "B":
                phys_port_list.append(hard_ware + ".B")  # 交换机有一个.B的物理端口
                physical_ports_information[hard_ware + ".B"] = [
                    "AswPhysPort",  # 物理端口类型
                    None,  # 物理端口标识符
                    hard_ware + ".B",  # 物理端口名称
                    None,
                    None,
                    "Bidirection",  # 物理端口方向
                    hard_ware  # 物理设备名称
                ]
            for phys_port_node in phys_port_nodes:
                if phys_port_node.nodeName != "#text":
                    physical_ports_information[hard_ware + "." + phys_port_node.getAttribute("Name")] = [
                        phys_port_node.nodeName,  # 物理端口类型
                        phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                        hard_ware + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                        phys_port_node.getAttribute("NameDef"),
                        phys_port_node.getAttribute("GuidDef"),
                        physical_ports_direction[phys_port_node.getAttribute("GuidDef")],  # 物理端口方向
                        hard_ware  # 物理设备名称
                    ]
                    if phys_port_node.nodeName != "PwrPhysPort":  # 电源接口不必统计在交换机信息哈希表中
                        phys_port_list.append(hard_ware + "." + phys_port_node.getAttribute("Name"))
            switches_information[self.root_node.getAttribute("Guid")] = [
                hard_ware,
                self.root_node.getAttribute("NameDef"),
                self.root_node.getAttribute("GuidDef"),
                phys_port_list
            ]
        elif self.root_node.nodeName == "CCR":  # 物理设备为CCR机柜
            device_nodes = self.root_node.childNodes
            for device_node in device_nodes:
                if device_node.nodeName == "ACS":  # 该设备为远端交换机
                    class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + device_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
                    get_direction = GET_DIRECTION(class_xml_file)
                    physical_ports_direction = get_direction.get_direction()
                    phys_port_nodes = device_node.childNodes
                    phys_port_list = []
                    if device_node.getAttribute("Name") in ["ACS_LA", "ACS_RA"]:
                        phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A")
                        physical_ports_information[self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A"] = [
                            "AswPhysPort",  # 物理端口类型
                            None,  # 物理端口标识符
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A",
                            # 物理端口名称
                            None,
                            None,
                            "Bidirection",  # 物理端口方向
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name")  # 物理设备名称
                        ]
                    if device_node.getAttribute("Name") in ["ACS_LB", "ACS_RB"]:
                        phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B")
                        physical_ports_information[self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B"] = [
                            "AswPhysPort",  # 物理端口类型
                            None,  # 物理端口标识符
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B",
                            # 物理端口名称
                            None,
                            None,
                            "Bidirection",  # 物理端口方向
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name")  # 物理设备名称
                        ]
                    for phys_port_node in phys_port_nodes:
                        if phys_port_node.nodeName != "#text":
                            physical_ports_information[hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name")] = [
                                phys_port_node.nodeName,  # 物理端口类型
                                phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                                hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                                phys_port_node.getAttribute("NameDef"),
                                phys_port_node.getAttribute("GuidDef"),
                                physical_ports_direction[phys_port_node.getAttribute("GuidDef")], # 物理端口方向
                                self.root_node.getAttribute("Name")  # 物理设备名称
                            ]
                            if phys_port_node.nodeName != "PwrPhysPort":  # 电源接口不必统计在交换机信息哈希表中
                                phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name"))
                    switches_information[device_node.getAttribute("Guid")] = [
                        device_node.getAttribute("Name"),
                        device_node.getAttribute("NameDef"),
                        device_node.getAttribute("GuidDef"),
                        phys_port_list
                    ]
                elif device_node.nodeName == "ARS":  # 该设备为远端交换机
                    class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + device_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
                    get_direction = GET_DIRECTION(class_xml_file)
                    physical_ports_direction = get_direction.get_direction()
                    phys_port_nodes = device_node.childNodes
                    phys_port_list = []
                    if device_node.getAttribute("Name") in ["ARS_LA", "ARS_RA"]:
                        phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A")
                        physical_ports_information[self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A"] = [
                            "AswPhysPort",  # 物理端口类型
                            None,  # 物理端口标识符
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".A",
                            # 物理端口名称
                            None,
                            None,
                            "Bidirection",  # 物理端口方向
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name")  # 物理设备名称
                        ]
                    if device_node.getAttribute("Name") in ["ARS_LB", "ARS_RB"]:
                        phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B")
                        physical_ports_information[self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B"] = [
                            "AswPhysPort",  # 物理端口类型
                            None,  # 物理端口标识符
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + ".B",
                            # 物理端口名称
                            None,
                            None,
                            "Bidirection",  # 物理端口方向
                            self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name")  # 物理设备名称
                        ]
                    for phys_port_node in phys_port_nodes:
                        if phys_port_node.nodeName != "#text":
                            physical_ports_information[hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name")] = [
                                phys_port_node.nodeName,  # 物理端口类型
                                phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                                hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                                phys_port_node.getAttribute("NameDef"),
                                phys_port_node.getAttribute("GuidDef"),
                                physical_ports_direction[phys_port_node.getAttribute("GuidDef")], # 物理端口方向
                                self.root_node.getAttribute("Name")  # 物理设备名称
                            ]
                            if phys_port_node.nodeName != "PwrPhysPort":  # 电源接口不必统计在交换机信息哈希表中
                                phys_port_list.append(self.root_node.getAttribute("Name") + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name"))
                    switches_information[device_node.getAttribute("Guid")] = [
                        device_node.getAttribute("Name"),
                        device_node.getAttribute("NameDef"),
                        device_node.getAttribute("GuidDef"),
                        phys_port_list
                    ]
                elif device_node.nodeName == "GPM":
                    class_xml_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + device_node.getAttribute("NameDef") + ".xml"  # 该Hardware文件对应的Class文件
                    get_direction = GET_DIRECTION(class_xml_file)
                    physical_ports_direction = get_direction.get_direction()
                    phys_port_nodes = device_node.childNodes
                    for phys_port_node in phys_port_nodes:
                        if phys_port_node.nodeName != "#text" and phys_port_node.nodeName != "GPMSchedule":
                            physical_ports_information[hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name")] = [
                                phys_port_node.nodeName,  # 物理端口类型
                                phys_port_node.getAttribute("Guid"),  # 物理端口标识符
                                hard_ware + "." + device_node.getAttribute("Name") + "." + phys_port_node.getAttribute("Name"),  # 物理端口名称
                                phys_port_node.getAttribute("NameDef"),
                                phys_port_node.getAttribute("GuidDef"),
                                physical_ports_direction[phys_port_node.getAttribute("GuidDef")], # 物理端口方向
                                self.root_node.getAttribute("Name")  # 物理设备名称
                            ]

        #physical_ports_index : 根据物理端口名称查询其在邻接矩阵中的下标
        #physical_ports_index_reversed : 根据物理端口在邻接矩阵中的下标，反向查询其物理端口的名称
        physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix = dict(), dict(), [ [0 for index1 in range(len(physical_ports_information))] for index2 in range(len(physical_ports_information))]
        index = 0
        for key in physical_ports_information.keys():
            physical_ports_index[key] = index
            physical_ports_index_reversed[index] = key
            index += 1
        return physical_ports_information, switches_information, RDIU_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix

    def parse_hosted_applications_and_hosted_functions(self, messages_tx, messages_rx, ref_table):
        """
        统计所有物理设备上消息的信息，物理设备上有两种类型的端口：物理端口与逻辑端口：
        物理端口，即上述中的：AswPhysPort, AesPhysPort, CANPhysPort, AnalogPhysPort, A429PhysPort, PwrPhysPort等端口；
        逻辑端口，是指：物理设备一般在逻辑上被划分为不同的分区，对应Hosted Applications, Hosted Functions。每一个分区（Hosted Application, Hosted Function）实现一种功能，相应地要进行信息的收发，逻辑端口即负责信息的收发功能。
        一个逻辑端口要么负责信息的收功能，要么进行信息的发功能，功能上不会重复。一般而言，一个逻辑端口只负责一条消息的收或发，但是也有例外，存在同一个逻辑端口收多条来自不同逻辑端口的消息。
        不同Hosted Application与Hosted Function的xml文件的结构差别很大，相应的，消息的分布也不同，因此需要结合消息的所有分布情况，分类进行考虑、统计。下面给出示例：
        1:
        <A653ApplicationComponent ...>
            <A653QueuingPort ...>
                <RP ...">
                    <Pub_Ref SrcName="HF_RIU_1.po429_RIU_GEN2_Aperiodic_Msg" SrcGuid="a2784ce3c-95c0-4497-905c-ef3baa244bc6a" />
                </RP>
                ...
                <RP ...">
                    <Pub_Ref .../>
                </RP>
            </A653QueuingPort>
            ...
            <A653SamplingPort ...>
                <A664Message ...>
                    <DS ...>
                        <DP Name="FSB1_L270" Guid="a8f18e60b-3bf0-42c9-b843-9bc7ccadae44a" NameDef="APP_AOC_CLASS.AOC_STATUS_LABEL_270.FSS1_L270.FSB1_L270" GuidDef="a6e5627e2-6288-4ccf-9575-e2ab52b0fe1aa" />
                    </DS>
                    <DS ...>
                        <DP ... />
                        <A429Word ...>
                            <DP ... />
                            ...
                            <DP ... />
                        </A429Word>
                    </DS>
                </A664Message>
            </A653SamplingPort>
        </A653ApplicationComponent>
        即：如果根节点的标签为：A653ApplicationComponent时，其子节点为A653SamplingPort或A653QueuingPort，可以为发送端口，也可以为接收端口，相应地其内部的消息有两种情况需要考虑：
        A653SamplingPort或A653QueuingPort为发送端口：
        653SamplingPort或A653QueuingPort为接收端口：

        2,
        <HostedFunction>
            <CANPort>
                <CANMessage>
                    ...
                </CANMessage>
                ...
                <CANMessage>
                    ...
                </CANMessage>
            </CANPort>
            <CANPort>
                <RP>
                    <Pub_Ref .../>
                    ...
                    <Pub_Ref .../>
                </RP>
                ...
                <RP>
                    <Pub_Ref .../>
                    ...
                    <Pub_Ref .../>
                </RP>
            <CANPort>
            ...
            <AnalogPort>
                <AnalogDiscreteParameter>
                    ...
                </AnalogDiscreteParameter>
            </AnalogPort>
            <A429Port>
                <RP>
                    <Pub_Ref ...>
                </RP>
            </A429Port>
            <A429Port>
                <A429Channel>
                    <A429Word>
                    ...
                    </A429Word>
                </A429Channel>
            </A429Port>

        </HostedFunction>
        """
        class_file = self.xml_file[:self.xml_file.find("Instances")] + "Classes/" + self.root_node.getAttribute("NameDef") + ".xml"  # 该Function or Application文件对应的Class文件
        hard_ware = self.root_node.getAttribute("Hardware")
        get_messagesize_syslatencywclimit_and_physicalport = GET_MESSAGESIZE_SYSLATENCYWCLIMIT_AND_PHYSICALPORT(class_file, hard_ware)
        tx_port_attribute, rx_port_attribute = get_messagesize_syslatencywclimit_and_physicalport.get_logical_port_attribute()

        logical_port_nodes = self.root_node.childNodes
        for logical_port_node in logical_port_nodes:
            if logical_port_node.nodeName == "#text":  # 无需考虑
                continue
            if logical_port_node.nodeName == "GP":  # 无需考虑
                continue
            if logical_port_node.hasChildNodes() == False:
                continue
            #因为<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>均是回填回去的，因此若存在<RP>标签，则一定在<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>这三个标签之前
            if logical_port_node.childNodes[1].nodeName == "Ep_Ref":  # 此类型消息无需考虑
                continue
            elif logical_port_node.childNodes[1].nodeName == "Emb_Ref":  # 此类型消息无需考虑
                continue
            elif logical_port_node.childNodes[1].nodeName == "Reversion_Ref":  # 此类型消息无需考虑
                continue
            elif logical_port_node.childNodes[1].nodeName != "RP":  # 发送端口
                if logical_port_node.nodeName in ["A653SamplingPort", "A653QueuingPort", "HFSamplingPort", "HFQueuingPort"]:
                    message_type = "A664"
                    message_size = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][0]  # 消息大小
                    physical = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息的发送物理端口名称
                    TransmissionIntervalMinimum = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][2]  # 消息的发送周期
                elif logical_port_node.nodeName == "CANPort":
                    message_type = "CAN"
                    message_size = 64  # 消息大小
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                    TransmissionIntervalMinimum = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息的发送周期
                elif logical_port_node.nodeName == "A429Port":
                    message_type = "A429"
                    message_size = 32  # 消息大小
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                    TransmissionIntervalMinimum = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息的发送周期
                elif logical_port_node.nodeName == "AnalogPort":
                    message_type = "Analog"
                    message_size = 16  # 消息大小
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                    TransmissionIntervalMinimum = tx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息的发送周期
                else:
                    print("Message type: None", self.xml_file, logical_port_node.childNodes[1].getAttribute("Guid"))
                    message_type, message_size, physical, TransmissionIntervalMinimum = "None", "None", ["None"], "None"  # 暂时不确定是否有其他格式的消息
                message_node = logical_port_node.childNodes[1]
                """
                这里，messages_tx，其
                键值（key）：消息的标识符（Guid）
                值（value）：列表，按顺序包括[ 消息的类型, 消息的大小, 消息的名称, 消息的所在物理设备名称, 消息的发送物理端口名称, 消息的发送逻辑端口标识符, 消息的发送逻辑端口名称, 消息的发送周期 ]
                """
                messages_tx[message_node.getAttribute("Guid")] = [message_type,  # 消息类型
                                                                  message_size,  # 消息大小
                                                                  message_node.getAttribute("Name"),  # 消息名称
                                                                  hard_ware,  # 消息的所在物理设备名称
                                                                  physical,  # 消息的发送物理端口名称
                                                                  logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                  logical_port_node.getAttribute("Name"), # 消息的发送逻辑端口名称
                                                                  TransmissionIntervalMinimum #消息的发送周期
                                                                  ]
                if message_node.hasChildNodes() == False:
                    continue
                """
                这里，ref_table，其
                键值（key）：包括：消息的标识符（Guid）, DS的标识符, DP的标识符
                值（value）：列表，按顺序包括[ 消息的标识符, 消息的名称, 消息的发送逻辑端口标识符, 消息的发送逻辑端口名称 ]
                目的是根据消息接收端的Pub_Ref标签的SrcGuid反向查找到消息的发送来源
                """
                ref_table[message_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),  # 对应消息的标识符
                                                                logical_port_node.childNodes[1].getAttribute("Name"),# 消息的名称
                                                                logical_port_node.getAttribute("Guid"),  # 消息的发送逻辑端口标识符
                                                                logical_port_node.getAttribute("Name")  # 消息的发送逻辑端口名称
                                                                ]
                if message_node.childNodes[1].nodeName != "DP":
                    dataset_nodes = message_node.childNodes
                    for dataset_node in dataset_nodes:
                        if dataset_node.nodeName == "#text":
                            continue
                        ref_table[dataset_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),  # 对应消息的标识符
                                                                        logical_port_node.childNodes[1].getAttribute("Name"),  # 消息的名称
                                                                        logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                        logical_port_node.getAttribute("Name")# 消息的发送逻辑端口名称
                                                                        ]
                        DP_nodes = dataset_node.childNodes
                        for DP_node in DP_nodes:
                            if DP_node.nodeName == "#text":
                                continue
                            if DP_node.nodeName == "DP":
                                ref_table[DP_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),# 对应消息的标识符
                                                                           logical_port_node.childNodes[1].getAttribute("Name"),  # 消息的名称
                                                                           logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                           logical_port_node.getAttribute("Name")# 消息的发送逻辑端口名称
                                                                           ]
                            else:
                                ref_table[DP_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),# 对应消息的标识符
                                                                           logical_port_node.childNodes[1].getAttribute("Name"),  # 消息的名称
                                                                           logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                           logical_port_node.getAttribute("Name")# 消息的发送逻辑端口名称
                                                                           ]
                                word_nodes = DP_node.childNodes
                                for word_node in word_nodes:
                                    if word_node.nodeName == "#text":
                                        continue
                                    ref_table[word_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),# 对应消息的标识符
                                                                                 logical_port_node.childNodes[1].getAttribute("Name"),  # 消息的名称
                                                                                 logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                                 logical_port_node.getAttribute("Name")# 消息的发送逻辑端口名称
                                                                                 ]
                else:
                    DP_nodes = message_node.childNodes
                    for DP_node in DP_nodes:
                        if DP_node.nodeName == "#text":
                            continue
                        ref_table[DP_node.getAttribute("Guid")] = [message_node.getAttribute("Guid"),  # 对应消息的标识符
                                                                   logical_port_node.childNodes[1].getAttribute("Name"),# 消息的名称
                                                                   logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                   logical_port_node.getAttribute("Name")  # 消息的发送逻辑端口名称
                                                                   ]
            else:  # 接收端口
                if logical_port_node.hasChildNodes() == False:
                    continue
                if logical_port_node.nodeName in ["A653SamplingPort", "A653QueuingPort", "HFSamplingPort","HFQueuingPort"]:
                    message_type = "A664"
                    message_size = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][0]  # 消息大小
                    latency_limit = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][2]  # 消息延迟要求
                    physical = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息的发送物理端口名称
                elif logical_port_node.nodeName == "CANPort":
                    message_type = "CAN"
                    message_size = 64  # 消息大小
                    latency_limit = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息延迟要求
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                elif logical_port_node.nodeName == "A429Port":
                    message_type = "A429"
                    message_size = 32  # 消息大小
                    latency_limit = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息延迟要求
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                elif logical_port_node.nodeName == "AnalogPort":
                    message_type = "Analog"
                    message_size = 16  # 消息大小
                    latency_limit = rx_port_attribute[logical_port_node.getAttribute("GuidDef")][1]  # 消息延迟要求
                    physical = [logical_port_node.getAttribute("Physical")]  # 消息的发送物理端口名称
                else:
                    print("Message type: None", self.xml_file, logical_port_node.childNodes[1].getAttribute("Guid"))
                    message_type, message_size, latency_limit, physical = "None", "None", "None", ["None"]  # 暂时不确定是否有其他格式的消息
                RP_nodes = logical_port_node.childNodes
                for RP_node in RP_nodes:
                    if RP_node.nodeName == "#text":
                        continue
                    if RP_node.nodeName == "Pub_Ref":
                        print("***********************************************************")
                        """
                        这里，messages_rx，其
                        键值（key）：消息接收端的Pub_Ref标签的SrcGuid标识符
                        值（value）：列表，按顺序包括[ 接收消息的类型, 接收消息的大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称 ]
                        """
                        messages_rx[RP_node.getAttribute("SrcGuid")] = [message_type,  # 消息类型
                                                                        message_size,  # 消息大小
                                                                        latency_limit,  # 消息延迟要求
                                                                        hard_ware,  # 消息的所在物理设备名称
                                                                        physical,  # 消息的发送物理端口名称
                                                                        logical_port_node.getAttribute("Guid"),
                                                                        # 消息的发送逻辑端口标识符
                                                                        logical_port_node.getAttribute("Name")
                                                                        # 消息的发送逻辑端口名称
                                                                        ]
                    else:
                        if RP_node.getElementsByTagName("Pub_Ref") == []:
                            continue
                        Pub_Ref_nodes = RP_node.getElementsByTagName("Pub_Ref")
                        for Pub_Ref_node in Pub_Ref_nodes:
                            messages_rx[Pub_Ref_node.getAttribute("SrcGuid")] = [message_type,  # 消息类型
                                                                                 message_size,  # 消息大小
                                                                                 latency_limit,  # 消息延迟要求
                                                                                 hard_ware,  # 消息的所在物理设备名称
                                                                                 physical,  # 消息的发送物理端口名称
                                                                                 logical_port_node.getAttribute("Guid"),# 消息的发送逻辑端口标识符
                                                                                 logical_port_node.getAttribute("Name")# 消息的发送逻辑端口名称
                                                                                 ]
        return messages_tx, messages_rx, ref_table

    def parse_logical_busses(self, physical_ports_information, physical_ports_index, physical_ports_adjacent_matrix):
        if self.root_node.nodeName == "LogicalBuses":  # Logical Busses xml文件
            LB_nodes = self.root_node.childNodes  # LB_nodes: DOM-tree的子节点列表，包括所有Logical Busses标签
            for LB_node in LB_nodes:
                if LB_node.nodeName != "#text":
                    physical_port_nodes = LB_node.getElementsByTagName("Port_Ref")
                    SOURCE, DESTINATION = [], []
                    for index in range(len(physical_port_nodes)):
                        if physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Bidirection":
                            SOURCE.append(physical_port_nodes[index].getAttribute("Name"))
                            DESTINATION.append(physical_port_nodes[index].getAttribute("Name"))
                        elif physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Source":
                            SOURCE.append(physical_port_nodes[index].getAttribute("Name"))
                        elif physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Destination":
                            DESTINATION.append(physical_port_nodes[index].getAttribute("Name"))
                    for source in SOURCE:
                        for destination in DESTINATION:
                            if source != destination:
                                source_index, destination_index = physical_ports_index[source], physical_ports_index[destination]
                                physical_ports_adjacent_matrix[source_index][destination_index] = 1
        else:  # CCR xml文件
            device_nodes = self.root_node.childNodes
            for device_node in device_nodes:
                if device_node.nodeName == "LB":  # 记录Logical Busses信息的标签
                    physical_port_nodes = device_node.getElementsByTagName("Port_Ref")
                    SOURCE, DESTINATION = [], []
                    for index in range(len(physical_port_nodes)):
                        if physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Bidirection":
                            SOURCE.append(physical_port_nodes[index].getAttribute("Name"))
                            DESTINATION.append(physical_port_nodes[index].getAttribute("Name"))
                        elif physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Source":
                            SOURCE.append(physical_port_nodes[index].getAttribute("Name"))
                        elif physical_ports_information[physical_port_nodes[index].getAttribute("Name")][5] == "Destination":
                            DESTINATION.append(physical_port_nodes[index].getAttribute("Name"))
                    for source in SOURCE:
                        for destination in DESTINATION:
                            if source != destination:
                                source_index, destination_index = physical_ports_index[source], physical_ports_index[
                                    destination]
                                physical_ports_adjacent_matrix[source_index][destination_index] = 1
        return physical_ports_adjacent_matrix

class GET_DIRECTION:
    # 根据传入的xml_file，记录物理端口的传输方向：None、Destination、Source或者Bidirection (其中：None针对电源接口PwrPhysPort)
    def __init__(self, class_xml_file):
        self.class_xml_file = class_xml_file
        self.DOMTree = parse(self.class_xml_file)
        self.root_node = self.DOMTree.documentElement

    # physical_ports_direction: 字典, 键值为物理端口类的Guid，亦即物理端口的GuidDef；value为direction：None、Destination、Source或者Bidirection (其中：None针对电源接口PwrPhysPort)
    def get_direction(self):
        physical_ports_direction = dict()
        physical_ports_nodes = self.root_node.childNodes
        for physical_ports_node in physical_ports_nodes:
            if physical_ports_node.nodeName != "#text":
                if physical_ports_node.nodeName == "AnalogPhysPort":
                    physical_ports_direction[
                        physical_ports_node.getAttribute("Guid")] = physical_ports_node.getAttribute("Direction")
                elif physical_ports_node.nodeName == "A429PhysPort":
                    physical_ports_direction[
                        physical_ports_node.getAttribute("Guid")] = physical_ports_node.getAttribute("Direction")
                elif physical_ports_node.nodeName == "CANPhysPort":
                    physical_ports_direction[physical_ports_node.getAttribute("Guid")] = "Bidirection"
                elif physical_ports_node.nodeName == "AswPhysPort":
                    physical_ports_direction[physical_ports_node.getAttribute("Guid")] = "Bidirection"
                elif physical_ports_node.nodeName == "AesPhysPort":
                    physical_ports_direction[physical_ports_node.getAttribute("Guid")] = "Bidirection"
                elif physical_ports_node.nodeName == "PwrPhysPort":
                    physical_ports_direction[physical_ports_node.getAttribute("Guid")] = "None"
        return physical_ports_direction

class GET_MESSAGESIZE_SYSLATENCYWCLIMIT_AND_PHYSICALPORT:
    def __init__(self, class_xml_file, hard_ware):
        self.class_xml_file = class_xml_file
        self.hard_ware = hard_ware  # 该应用的驻留物理设备
        self.DOMTree = parse(self.class_xml_file)
        self.root_node = self.DOMTree.documentElement

    def get_logical_port_attribute(self):
        #因为消息的大小、延迟要求是与logical port对应的，因此，这里定义的两个用于查询的字典，其键值均为class文件中logical port的标识符
        tx_port_attribute, rx_port_attribute = dict(), dict()
        logical_port_nodes = self.root_node.childNodes
        for logical_port_node in logical_port_nodes:
            if logical_port_node.nodeName in ["A653SamplingPort", "A653QueuingPort", "HFSamplingPort", "HFQueuingPort"]:
                if logical_port_node.hasChildNodes() == False:
                    continue
                message_size, physical_port = int(logical_port_node.getAttribute("MessageSize")), []
                if logical_port_node.getAttribute("Networks") == "Both":
                    physical_port.append(self.hard_ware + ".A")
                    physical_port.append(self.hard_ware + ".B")
                elif logical_port_node.getAttribute("Networks") == "A":
                    physical_port.append(self.hard_ware + ".A")
                else:
                    physical_port.append(self.hard_ware + ".B")
                #因为<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>均是回填回去的，因此若存在<RP>标签，则一定在<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>这三个标签之前
                if logical_port_node.childNodes[1].nodeName == "Ep_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName == "Emb_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName == "Reversion_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName != "RP":  # 发送端口
                    #TransmissionIntervalMinimum: 传输周期(间隔),其倒数为频率
                    TransmissionIntervalMinimum = float(logical_port_node.childNodes[1].getAttribute("TransmissionIntervalMinimum"))
                    tx_port_attribute[logical_port_node.getAttribute("Guid")] = [message_size, physical_port, TransmissionIntervalMinimum]
                else:
                    RP_node = logical_port_node.getElementsByTagName("RP")[0]
                    if RP_node.getAttribute("SysLatencyWCLimit") == "0":
                        syslantencywclimit = 9223372036854775807
                    else:
                        syslantencywclimit = int(RP_node.getAttribute("SysLatencyWCLimit"))
                    rx_port_attribute[logical_port_node.getAttribute("Guid")] = [message_size, physical_port, syslantencywclimit]
            elif logical_port_node.nodeName in ["CANPort", "A429Port", "AnalogPort"]:
                if logical_port_node.hasChildNodes() == False:
                    continue
                if logical_port_node.nodeName == "CANPort":
                    message_size = 64
                elif logical_port_node.nodeName == "A429Port":
                    message_size = 32
                else:
                    message_size = 16
                #因为<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>均是回填回去的，因此若存在<RP>标签，则一定在<Ep_Ref>, <Emb_Ref>, <Reversion_Ref>这三个标签之前
                if logical_port_node.childNodes[1].nodeName == "Ep_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName == "Emb_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName == "Reversion_Ref":  # 此类型消息无需考虑
                    continue
                elif logical_port_node.childNodes[1].nodeName != "RP":  # 发送端口
                    # TransmissionIntervalMinimum: 传输周期(间隔),其倒数为频率
                    #因为离散量AnalogPort的发送周期暂时没有查询到，所以现已"None"代替
                    if logical_port_node.nodeName == "AnalogPort":
                        TransmissionIntervalMinimum = "None"
                    else:
                        TransmissionIntervalMinimum = float(logical_port_node.childNodes[1].getAttribute("TransmissionIntervalMinimum"))
                    tx_port_attribute[logical_port_node.getAttribute("Guid")] = [message_size, TransmissionIntervalMinimum]
                else:
                    RP_node = logical_port_node.getElementsByTagName("RP")[0]
                    if RP_node.getAttribute("SysLatencyWCLimit") == "0":
                        syslantencywclimit = 9223372036854775807
                    else:
                        syslantencywclimit = int(RP_node.getAttribute("SysLatencyWCLimit"))
                    rx_port_attribute[logical_port_node.getAttribute("Guid")] = [message_size, syslantencywclimit]
            else:
                continue

        return tx_port_attribute, rx_port_attribute

class COUNT_MESSAGES_PER_PHYSICALPORT:
    """
    统计各个A664端口（AesPhysPort）的消息信息，并以如下数据结构存储：
    messages_per_physical_port = dict()
    键值（key）：物理端口名称
    值（value）：以列表形式存储，按顺序包括：[ physical port name, [type_of_message1, ..., type_of_messagen ] [ size_of_message1, ..., size_of_messagen ], [latency_of_message1, ..., latency_of_messagen], [TransmissionIntervalMinimum_of_message1, ..., TransmissionIntervalMinimum_of_messagen] ]
    """

    def __init__(self, messages_info):
        self.messages_info = messages_info

    """
    字典messages_info
    键值（key）：消息的标识符
    值（value）：列表，按顺序包括[
        发送端消息类型, #0
        发送端消息大小, #1
        发送端消息名称, #2
        发送端消息所在物理设备, #3
        发送端物理端口名称, #-->列表
        发送端逻辑端口标识符, #4
        发送端逻辑端口名称, #6
        消息的发送周期 #7
        [接收端逻辑端口], # 用于判断是否重复添加接收信息 #8
        [
            [接收消息类型 #0, 接收消息大小 #1, 接收消息的延迟要求 #2, 接收消息的所在物理设备名称 #3, 接收消息的物理端口名称 #4-->列表, 消息的接收逻辑端口标识符 #5, 消息的接收逻辑端口名称 #6],
            ...                                                                                                                                                  #9
            [接收消息类型, 接收消息大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称]
        ]
    ]
    """
    def count_messages(self, physical_ports_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix):
        messages_per_physical_port = dict()
        TOTAL = 0
        for message_guid in list(self.messages_info.keys()):
            if self.messages_info[message_guid][0] == "A664":  # ARINC664消息
                for physical_port_name in self.messages_info[message_guid][4]:  # 因为消息可能从A, B网同时进行传输，所以这里消息的物理发送端口是一列表，其中有可能包括两个端口
                    if physical_port_name in messages_per_physical_port:
                        messages_per_physical_port[physical_port_name][1].append("A664")
                        messages_per_physical_port[physical_port_name][2].append(self.messages_info[message_guid][1])
                        min_latency = self.messages_info[message_guid][9][0][2]
                        for index in range(len(self.messages_info[message_guid][9])):
                            min_latency = min(min_latency, self.messages_info[message_guid][9][index][2])
                        messages_per_physical_port[physical_port_name][3].append(min_latency)
                        TransmissionIntervalMinimum = [self.messages_info[message_guid][7]]
                        messages_per_physical_port[physical_port_name][4].append(TransmissionIntervalMinimum)
                    else:
                        message_type, message_size = ["A664"], [self.messages_info[message_guid][1]]
                        min_latency = self.messages_info[message_guid][9][0][2]
                        for index in range(len(self.messages_info[message_guid][9])):
                            min_latency = min(min_latency, self.messages_info[message_guid][9][index][2])
                        message_latency = [min_latency]
                        TransmissionIntervalMinimum = [self.messages_info[message_guid][7]]
                        messages_per_physical_port[physical_port_name] = [physical_port_name, message_type, message_size, message_latency, TransmissionIntervalMinimum]
            else:  # 非ARINC664消息
                total = 0
                for physical_port_name in self.messages_info[message_guid][4]:
                    for index in range(len(physical_ports_adjacent_matrix[0])):
                        if physical_ports_adjacent_matrix[physical_ports_index[physical_port_name]][index] == 1:  # 说明此非664消息经物理端口physical_port_name向RDIU中下标为index的物理端口传输数据
                            if physical_ports_information[physical_ports_index_reversed[index]][6][0:4] == "RDIU":  # 下标为index的物理端口所在物理设备为RDIU
                                total += 1
                                RDIU_name = physical_ports_information[physical_ports_index_reversed[index]][6] #该物理端口所在物理设备的名称，即RDIU的名称
                                if RDIU_name in messages_per_physical_port:
                                    messages_per_physical_port[RDIU_name][1].append(self.messages_info[message_guid][0])
                                    messages_per_physical_port[RDIU_name][2].append(self.messages_info[message_guid][1])
                                    min_latency = self.messages_info[message_guid][9][0][2]
                                    for index in range(len(self.messages_info[message_guid][9])):
                                        min_latency = min(min_latency, self.messages_info[message_guid][9][index][2])
                                    messages_per_physical_port[RDIU_name][3].append(min_latency)
                                    TransmissionIntervalMinimum = [self.messages_info[message_guid][7]]
                                    messages_per_physical_port[RDIU_name][4].append(TransmissionIntervalMinimum)
                                else:
                                    message_type, message_size = [self.messages_info[message_guid][0]], [self.messages_info[message_guid][1]]
                                    min_latency = self.messages_info[message_guid][9][0][2]
                                    for index in range(len(self.messages_info[message_guid][9])):
                                        min_latency = min(min_latency, self.messages_info[message_guid][9][index][2])
                                    message_latency = [min_latency]
                                    TransmissionIntervalMinimum = [self.messages_info[message_guid][7]]
                                    messages_per_physical_port[RDIU_name] = [RDIU_name, message_type, message_size,message_latency, TransmissionIntervalMinimum]
        # print("TOTAL:", TOTAL) # 存在非664消息被同时传输至两个RDIU的情况，因此TOTAL是记录被同时传输至两个RDIU设备的消息的数目
        return messages_per_physical_port

class MERGE_TX_MESSAGES_AND_RX_MESSAGES:
    def merge_messages(self, messages_tx, messages_rx, ref_table):
        """
        首先看一下messages_tx, ref_table, messages_rx这三个字典的结构：
        messages_tx:
            这里，messages_tx，其
                键值（key）：消息的标识符（Guid）
                值（value）：列表，按顺序包括[ 消息的类型, 消息的大小, 消息的名称, 消息的所在物理设备名称, 消息的发送物理端口名称, 消息的发送逻辑端口标识符, 消息的发送逻辑端口名称, 消息的发送间隔 ]
        ref_table:
            这里，ref_table，其
                键值（key）：包括：消息的标识符（Guid）, DS的标识符, DP的标识符
                值（value）：列表，按顺序包括[ 消息的标识符, 消息的名称, 消息的发送逻辑端口标识符, 消息的发送逻辑端口名称 ]
                目的是根据消息接收端的Pub_Ref标签的SrcGuid反向查找到消息的发送来源
        messages_rx:
            这里，messages_rx，其
                    键值（key）：消息接收端的Pub_Ref标签的SrcGuid标识符
                    值（value）：列表，按顺序包括[ 接收消息的类型, 接收消息的大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称 ]
        因此，为将消息的发送端与接收端联系起来，建立完整的关系，决定建立以下数据结构：
        字典messages_info
        键值（key）：消息的标识符
        值（value）：列表，按顺序包括[
            发送端消息类型, #0
            发送端消息大小, #1
            发送端消息名称, #2
            发送端消息所在物理设备, #3
            发送端物理端口名称, #-->列表
            发送端逻辑端口标识符, #4
            发送端逻辑端口名称, #6
            消息的发送周期 #7
            [接收端逻辑端口], # 用于判断是否重复添加接收信息 #8
            [
                [接收消息类型 #0, 接收消息大小 #1, 接收消息的延迟要求 #2, 接收消息的所在物理设备名称 #3, 接收消息的物理端口名称 #4-->列表, 消息的接收逻辑端口标识符 #5, 消息的接收逻辑端口名称 #6],
                ...                                                                                                                                                  #9
                [接收消息类型, 接收消息大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称]
            ]
        ]
        """
        messages_info = dict()

        for message_rx_guid in list(messages_rx.keys()):
            ref_table_value = ref_table[message_rx_guid]
            message_guid = ref_table_value[0]  # 消息的标识符
            if message_guid in messages_info:  # 此消息已经建立过一次关系
                if messages_rx[message_rx_guid][4] == messages_tx[message_guid][4]:
                    continue
                # 首先判断接收端逻辑端口是否已被统计过
                if messages_rx[message_rx_guid][5] in messages_info[message_guid][8]:
                    continue
                else:
                    messages_info[message_guid][8].append(messages_rx[message_rx_guid][5])
                    info_rx = []
                    for item in messages_rx[message_rx_guid]:
                        info_rx.append(item)  # 添加以下信息：接收消息类型, 接收消息大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称
                    messages_info[message_guid][9].append(info_rx)
            else:  # 此消息尚未建立过关系
                #存在这样一种消息：消息的发送端物理端口和接收端物理端口相同，说明该消息为一个Loopback消息（即：物理设备内自发自收），无需经过AFDX网络路由，因此不予考虑
                if messages_rx[message_rx_guid][4] == messages_tx[message_guid][4]:
                    continue
                message_info = []
                for item in messages_tx[message_guid]:
                    message_info.append(item)  # 添加以下信息：发送端消息类型, 发送端消息大小, 发送端消息名称, 发送端消息所在物理设备, 发送端物理端口名称, 发送端逻辑端口标识符, 发送端逻辑端口名称, 消息的发送周期
                logical_ports_rx = [messages_rx[message_rx_guid][5]]
                message_info.append(logical_ports_rx)
                info_rx = []
                for item in messages_rx[message_rx_guid]:
                    info_rx.append(item)  # 添加以下信息：接收消息类型, 接收消息大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称
                message_info.append([info_rx])
                messages_info[message_guid] = message_info
        return messages_info

class GET_PHYSICAL_PORTS_ADJACENT_MATRIX:
    def __init__(self, root_path):
        self.root_path = root_path
        self.get_xml_path = GET_XML_PATH(self.root_path)

    def get_physical_ports_adjacent_matrix(self, physical_ports_information, switches_information, physical_ports_index, physical_ports_adjacent_matrix):
        xml_files_of_logical_busses = self.get_xml_path.get_xml_path_pf_logical_busses()
        for xml_file in xml_files_of_logical_busses:
            parse_xml = PARSE_XML(xml_file)
            physical_ports_adjacent_matrix = parse_xml.parse_logical_busses(physical_ports_information, physical_ports_index, physical_ports_adjacent_matrix)

        """
        除了Logical Busses文件中的物理端口连接关系，注意到还有交换机端口的内部连接关系，以及RDIU端口的内部连接关系
        这里首先完善交换机端口的内部连接关系
        再完善RDIU端口的内部连接关系
        """
        for key in list(switches_information.keys()):
            for physical_port1 in switches_information[key][3]:
                for physical_port2 in switches_information[key][3]:
                    if physical_port1 != physical_port2:
                        source_index, destination_index = physical_ports_index[physical_port1], physical_ports_index[physical_port2]
                        physical_ports_adjacent_matrix[source_index][destination_index] = 1

        return physical_ports_adjacent_matrix

class GET_ADJACENT_MATRIX_FOR_A_B_NET:
    def get_adjacent_matrix_for_a_b_net(self, physical_ports_information, physical_ports_index, physical_ports_adjacent_matrix):
        #虚拟链路VL只能在ARINC664协议的物理端口间传输，且区分A、B网
        #因此，单独建立、存储ARINC664协议的物理端口间的连接关系
        #首先统计ARINC664协议的物理端口的数目
        NUMBER_OF_ARINC664_PHYSICAL_PORTS = 0 #全网中ARINC664端口数目
        NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_A_NET, NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_A_NET, NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET, index_FOR_A_NET = 0, 0, 0, 0 #A网中交换机、终端、ARINC664端口的数目以及ARINC664端口的序号
        NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_B_NET, NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_B_NET, NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET, index_FOR_B_NET = 0, 0, 0, 0 #B网中交换机、终端、ARINC664端口的数目以及ARINC664端口的序号
        arinc664_physical_ports_index_for_A_NET, arinc664_physical_ports_index_reversed_for_A_NET = dict(), dict()
        arinc664_physical_ports_index_for_B_NET, arinc664_physical_ports_index_reversed_for_B_NET = dict(), dict()
        for key in physical_ports_information.keys():
            if physical_ports_information[key][0] == 'AesPhysPort' or physical_ports_information[key][0] == 'AswPhysPort':  # ARINC664协议物理端口
                NUMBER_OF_ARINC664_PHYSICAL_PORTS += 1
                #判断此ARINC664协议物理端口属于A网还是B网
                if physical_ports_information[key][0] == 'AesPhysPort': #终端
                    if physical_ports_information[key][2][-1] == 'A':  # 属于A网
                        arinc664_physical_ports_index_for_A_NET[key] = index_FOR_A_NET
                        arinc664_physical_ports_index_reversed_for_A_NET[index_FOR_A_NET] = key
                        index_FOR_A_NET += 1
                        NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_A_NET += 1
                        NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET += 1
                    elif physical_ports_information[key][2][-1] == 'B':  # 属于B网
                        arinc664_physical_ports_index_for_B_NET[key] = index_FOR_B_NET
                        arinc664_physical_ports_index_reversed_for_B_NET[index_FOR_B_NET] = key
                        index_FOR_B_NET += 1
                        NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_B_NET += 1
                        NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET += 1
                else: #交换机
                    if physical_ports_information[key][2][0:6] == 'ARS_1A' or \
                            physical_ports_information[key][2][0:6] == 'ARS_2A' or \
                            physical_ports_information[key][2][0:15] == 'CCR_LEFT.ACS_LA' or \
                            physical_ports_information[key][2][0:16] == 'CCR_RIGHT.ACS_RA':
                        arinc664_physical_ports_index_for_A_NET[key] = index_FOR_A_NET
                        arinc664_physical_ports_index_reversed_for_A_NET[index_FOR_A_NET] = key
                        index_FOR_A_NET += 1
                        NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_A_NET += 1
                        NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET += 1
                    elif physical_ports_information[key][2][0:6] == 'ARS_1B' or \
                            physical_ports_information[key][2][0:6] == 'ARS_2B' or \
                            physical_ports_information[key][2][0:15] == 'CCR_LEFT.ACS_LB' or \
                            physical_ports_information[key][2][0:16] == 'CCR_RIGHT.ACS_RB':
                        arinc664_physical_ports_index_for_B_NET[key] = index_FOR_B_NET
                        arinc664_physical_ports_index_reversed_for_B_NET[index_FOR_B_NET] = key
                        index_FOR_B_NET += 1
                        NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_B_NET += 1
                        NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET += 1
        print("Number of A664 physical ports:", NUMBER_OF_ARINC664_PHYSICAL_PORTS)
        print("Number of A664 physical ports for A net:", NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET)
        print("Number of A664 physical ports for B net:", NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET)
        print("Number of AES physical ports for A net:", NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_A_NET,"Number of AWS physical ports for A net:", NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_A_NET)
        print("Number of AES physical ports for B net:", NUMBER_OF_AES_ARINC664_PHYSICAL_PORTS_OF_B_NET,"Number of AWS physical ports for B net:", NUMBER_OF_ASW_ARINC664_PHYSICAL_PORTS_OF_B_NET)
        arinc664_physical_ports_adjacent_matrix_for_A_NET = [ [0 for index1 in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET)] for index2 in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET)]
        arinc664_physical_ports_adjacent_matrix_for_B_NET = [ [0 for index1 in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET)] for index2 in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET)]

        #完善A网络中，ARINC664协议的物理端口的邻接矩阵
        for row_index in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET):
            for column_index in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_A_NET):
                name_of_physical_port1 = arinc664_physical_ports_index_reversed_for_A_NET[row_index]
                name_of_physical_port2 = arinc664_physical_ports_index_reversed_for_A_NET[column_index]
                arinc664_physical_ports_adjacent_matrix_for_A_NET[row_index][column_index] = physical_ports_adjacent_matrix[physical_ports_index[name_of_physical_port1]][physical_ports_index[name_of_physical_port2]]
                arinc664_physical_ports_adjacent_matrix_for_A_NET[column_index][row_index] = physical_ports_adjacent_matrix[physical_ports_index[name_of_physical_port2]][physical_ports_index[name_of_physical_port1]]

        #完善B网络中，ARINC664协议的物理端口的邻接矩阵
        for row_index in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET):
            for column_index in range(NUMBER_OF_ARINC664_PHYSICAL_PORTS_FOR_B_NET):
                name_of_physical_port1 = arinc664_physical_ports_index_reversed_for_B_NET[row_index]
                name_of_physical_port2 = arinc664_physical_ports_index_reversed_for_B_NET[column_index]
                arinc664_physical_ports_adjacent_matrix_for_B_NET[row_index][column_index] = physical_ports_adjacent_matrix[physical_ports_index[name_of_physical_port1]][physical_ports_index[name_of_physical_port2]]
                arinc664_physical_ports_adjacent_matrix_for_B_NET[column_index][row_index] = physical_ports_adjacent_matrix[physical_ports_index[name_of_physical_port2]][physical_ports_index[name_of_physical_port1]]

        #保存文件
        np.save('arinc664_physical_ports_index_for_A_NET.npy', arinc664_physical_ports_index_for_A_NET)
        np.save('arinc664_physical_ports_index_for_B_NET.npy', arinc664_physical_ports_index_for_B_NET)
        np.save('arinc664_physical_ports_index_reversed_for_A_NET.npy', arinc664_physical_ports_index_reversed_for_A_NET)
        np.save('arinc664_physical_ports_index_reversed_for_B_NET.npy', arinc664_physical_ports_index_reversed_for_B_NET)
        #读取方式
        #arinc664_physical_ports_index_for_A_NET = np.load( 'arinc664_physical_ports_index_for_A_NET.npy', allow_pickle='TRUE').item()

        return arinc664_physical_ports_index_for_A_NET, arinc664_physical_ports_index_reversed_for_A_NET, arinc664_physical_ports_adjacent_matrix_for_A_NET, arinc664_physical_ports_index_for_B_NET, arinc664_physical_ports_index_reversed_for_B_NET, arinc664_physical_ports_adjacent_matrix_for_B_NET

class GENERATE_FILES_FOR_ROUTING:
    def __init__(self, arinc664_physical_ports_adjacent_matrix_for_A_NET, arinc664_physical_ports_adjacent_matrix_for_B_NET, switches_information, messages_info):
        self.arinc664_physical_ports_adjacent_matrix_for_A_NET = arinc664_physical_ports_adjacent_matrix_for_A_NET
        self.arinc664_physical_ports_adjacent_matrix_for_B_NET = arinc664_physical_ports_adjacent_matrix_for_B_NET
        self.switches_information = switches_information
        self.messages_info = messages_info

    #统计A、B网中物理链路的数目(包括交换机内部)
    def counting_connections_of_a_b_net(self):
        counting = 0
        for row_index in range( len( self.arinc664_physical_ports_adjacent_matrix_for_A_NET ) ):
            counting += np.sum( np.array( self.arinc664_physical_ports_adjacent_matrix_for_A_NET[row_index] ) )
        print( "Number of physical connections of net A:", counting )

        counting = 0
        for row_index in range( len( self.arinc664_physical_ports_adjacent_matrix_for_B_NET ) ):
            counting += np.sum( np.array( self.arinc664_physical_ports_adjacent_matrix_for_B_NET[row_index] ) )
        print("Number of connections of net B:", counting)

        print( "The number of switches is:", len( self.switches_information ) )

    #将AFDX网络连接关系的邻接矩阵、A网的邻接矩阵、B网的邻接矩阵以.txt的形式存储
    def save_connections_of_afdx(self):
        ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_A_SAVE_PATH = "ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_A.txt"
        fw2 = open(ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_A_SAVE_PATH, 'w+')
        for row_index in range(len(self.arinc664_physical_ports_adjacent_matrix_for_A_NET)):
            for column_index in range(len(self.arinc664_physical_ports_adjacent_matrix_for_A_NET)):
                if column_index == len(self.arinc664_physical_ports_adjacent_matrix_for_A_NET) - 1:
                    fw2.write("{}\n".format(self.arinc664_physical_ports_adjacent_matrix_for_A_NET[row_index][column_index]))
                else:
                    fw2.write("{}  ".format(self.arinc664_physical_ports_adjacent_matrix_for_A_NET[row_index][column_index]))
        fw2.close()

        ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_B_SAVE_PATH = "ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_B.txt"
        fw4 = open(ARINC664_PHYSICAL_PORTS_CONNECTIONS_OF_NET_B_SAVE_PATH, 'w+')
        for row_index in range(len(self.arinc664_physical_ports_adjacent_matrix_for_B_NET)):
            for column_index in range(len(self.arinc664_physical_ports_adjacent_matrix_for_B_NET)):
                if column_index == len(self.arinc664_physical_ports_adjacent_matrix_for_B_NET) - 1:
                    fw4.write("{}\n".format(self.arinc664_physical_ports_adjacent_matrix_for_B_NET[row_index][column_index]))
                else:
                    fw4.write("{}  ".format(self.arinc664_physical_ports_adjacent_matrix_for_B_NET[row_index][column_index]))
        fw4.close()

    """
    字典messages_info
    键值（key）：消息的标识符
    值（value）：列表，按顺序包括[
        发送端消息类型, #0
        发送端消息大小, #1
        发送端消息名称, #2
        发送端消息所在物理设备, #3
        发送端物理端口名称, #-->列表
        发送端逻辑端口标识符, #4
        发送端逻辑端口名称, #6
        消息的发送周期 #7
        [接收端逻辑端口], # 用于判断是否重复添加接收信息 #8
        [
            [接收消息类型 #0, 接收消息大小 #1, 接收消息的延迟要求 #2, 接收消息的所在物理设备名称 #3, 接收消息的物理端口名称 #4-->列表, 消息的接收逻辑端口标识符 #5, 消息的接收逻辑端口名称 #6],
            ...                                                                                                                                                  #9
            [接收消息类型, 接收消息大小, 接收消息的延迟要求, 接收消息的所在物理设备名称, 接收消息的物理端口名称, 消息的接收逻辑端口标识符, 消息的接收逻辑端口名称]
        ]
    ]
    """
    #将网络中的消息以.txt的形式存储
    def save_messages_of_afdx(self):
        ARINC664_MESSAGES_SAVE_PATH = "ARINC664_MESSAGES.txt"
        fw = open(ARINC664_MESSAGES_SAVE_PATH, 'w+')
        for key in self.messages_info.keys():
            if self.messages_info[key][0] == 'A664':
                fw.write("{} {}".format(self.messages_info[key][4], key))
                NUMBER_OF_DESTINATIONS = len(self.messages_info[key][9])  # 消息的接收端的数目
                for index in range(NUMBER_OF_DESTINATIONS):
                    fw.write("     {}  {}".format(self.messages_info[key][9][index][4], self.messages_info[key][9][index][5]))
                fw.write("\n")
        fw.close()

        ARINC664_MESSAGES_OF_NET_A_SAVE_PATH = "ARINC664_MESSAGES_OF_NET_A.txt"
        fw1 = open( ARINC664_MESSAGES_OF_NET_A_SAVE_PATH, 'w+')
        for key in self.messages_info.keys():
            if self.messages_info[ key ][0] == 'A664':
                if self.messages_info[ key ][4][0][-2:] != '.A': #发送端物理端口第一个不是A口，说明此消息仅从B网发送
                    continue
                else:
                    fw1.write( "{}".format( self.messages_info[ key ][4][0] ) )
                    NUMBER_OF_DESTINATIONS = len( self.messages_info[ key ][9] ) # 消息的接收端的数目
                    for index1 in range( NUMBER_OF_DESTINATIONS ):
                        for index2 in range( len( self.messages_info[ key ][9][index1][4] ) ):
                            if self.messages_info[ key ][9][index1][4][index2][-2:] == '.A':
                                fw1.write( "     {}".format( self.messages_info[ key ][9][index1][4][index2] ) )
                    fw1.write("\n")
        fw1.close()

        ARINC664_MESSAGES_OF_NET_B_SAVE_PATH = "ARINC664_MESSAGES_OF_NET_B.txt"
        fw3 = open( ARINC664_MESSAGES_OF_NET_B_SAVE_PATH, 'w+')
        for key in self.messages_info.keys():
            if self.messages_info[ key ][0] == 'A664':
                if len( self.messages_info[ key ][4] ) == 1:
                    if self.messages_info[key][4][0][-2:] != '.B':
                        continue
                    else:
                        fw3.write( "{}".format( self.messages_info[key][4][0] ) )
                        NUMBER_OF_DESTINATIONS = len( self.messages_info[key][9] )  # 消息的接收端的数目
                        for index1 in range(NUMBER_OF_DESTINATIONS):
                            for index2 in range(len(self.messages_info[key][9][index1][4])):
                                if self.messages_info[key][9][index1][4][index2][-2:] == '.B':
                                    fw3.write("     {}".format(self.messages_info[key][9][index1][4][index2]))
                        fw3.write("\n")
                else:
                    fw3.write( "{}".format( self.messages_info[ key ][4][1] ) )
                    NUMBER_OF_DESTINATIONS = len( self.messages_info[ key ][9] ) # 消息的接收端的数目
                    for index1 in range(NUMBER_OF_DESTINATIONS):
                        for index2 in range(len(self.messages_info[key][9][index1][4])):
                            if self.messages_info[key][9][index1][4][index2][-2:] == '.B':
                                fw3.write("     {}".format(self.messages_info[key][9][index1][4][index2]))
                    fw3.write("\n")
        fw3.close()