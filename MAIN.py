import FUNCTIONAL_CLASS
import numpy as np
import os

root_path = "Data Info/"

if __name__ == "__main__":

    """
    获取数据文件"Data Info"(即："root_path/"路径下)所有分系统下硬件设备（./Data Info/***/Hardware/Instances/**.xml）的端口信息、交换机信息以及物理端口连接关系的邻接矩阵
    physical_ports_information: 字典，键值为physical port full name，格式为: 设备+"."+物理端口名(如: IDURIGHTOUTBOARD.A)，或者: 机柜+"."+设备+"."+物理端口名(如: CCR_LEFT.GPM_L6.A)，value为: [物理端口类型, 物理端口标识符, physical port full name, NameDef, GuidDef, 物理端口方向, 该物理端口所在物理设备名称]
        注意：physical port full name与物理端口名不同，前者描述得更详细
    switches_information: 字典，键值为交换机的Guid，value为: [ 交换机名称(如：ARS_1A, CCR_LEFT.ACS_LA), NameDef, GuidDef, [ 25*[ physical port full name ] ] ]
    RDIU_information: 字典，
    physical_ports_index: 字典，键值为physical port的名称，如：CCR_LEFT.GPM_L6.A，value为：该端口在邻接矩阵中的index
    physical_ports_index_reversed: 字典，键值为端口在邻接矩阵中的index，value为：该端口的physical port的名称
    physical_ports_adjacent_matrix：所有物理端口的连接关系
    物理端口类型包括：'AesPhysPort', 'A429PhysPort', 'CANPhysPort', 'AnalogPhysPort', 'AswPhysPort', 'PwrPhysPort'共6种
    一个physical_ports_information的示例：['AnalogPhysPort', 'a0E324550-223F-4e9e-894A-3800179CFC38a', 'AFTBBSOV1.poDISC_FC', 'IAMS_VALVECLASS.poDISC_FC', 'a7E9EEF76-C9D3-48f9-B683-E65C3F3F4273a', 'Source', 'AFTBBSOV1']
    """
    get_info = FUNCTIONAL_CLASS.GET_INFO( root_path )
    physical_ports_information, switches_information, RDIU_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix = get_info.get_hardware_info()

    """
    完善物理端口连接关系的邻接矩阵
    AesPhysPort, AswPhysPort, CANPhysPort为双向
    A429PhysPort, AnalogPhysPort为单向
    一般而言，LB的两个（或三个）物理端口的关系是：
    ['Destination', 'Source']
    ['Source', 'Destination']
    ['Bidirection', 'Bidirection']
    ['Destination', 'Destination', 'Source']
    ['Source', 'Destination', 'Destination']
    ['Destination', 'Source', 'Destination', 'Destination']
    ['Source', 'Source', 'Destination']
    ['Source', 'Destination', 'Destination', 'Destination', 'Destination', 'Destination']
    ['Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection']
    ['Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection', 'Bidirection']
    ['Destination', 'Destination', 'Destination', 'Destination', 'Destination', 'Destination', 'Destination', 'Destination', 'Source']
    """
    get_physical_ports_adjacent_matrix = FUNCTIONAL_CLASS.GET_PHYSICAL_PORTS_ADJACENT_MATRIX( root_path )
    physical_ports_adjacent_matrix = get_physical_ports_adjacent_matrix.get_physical_ports_adjacent_matrix( physical_ports_information, switches_information, physical_ports_index, physical_ports_adjacent_matrix )

    #建立AFDX网络中A, B网内的ARINC664物理端口连接关系的邻接矩阵
    get_adjacent_matrix_for_a_b_net = FUNCTIONAL_CLASS.GET_ADJACENT_MATRIX_FOR_A_B_NET()
    arinc664_physical_ports_index_for_A_NET, arinc664_physical_ports_index_reversed_for_A_NET, arinc664_physical_ports_adjacent_matrix_for_A_NET, \
    arinc664_physical_ports_index_for_B_NET, arinc664_physical_ports_index_reversed_for_B_NET, arinc664_physical_ports_adjacent_matrix_for_B_NET = \
        get_adjacent_matrix_for_a_b_net.get_adjacent_matrix_for_a_b_net( physical_ports_information, physical_ports_index, physical_ports_adjacent_matrix )

    messages_tx, messages_rx, ref_table = get_info.get_hosted_applications_and_hosted_functions_info()
    merge_tx_messages_and_rx_messages = FUNCTIONAL_CLASS.MERGE_TX_MESSAGES_AND_RX_MESSAGES()
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
    messages_info = merge_tx_messages_and_rx_messages.merge_messages(messages_tx, messages_rx, ref_table)
    print("length of messages_info:", len(messages_info))
    """
    经检查，不存在：有收端消息的信息，却没有该消息在发端的信息
    for item in list(messages_rx.keys()):
        if item in ref_table:
            continue
        else:
            print( item )
    """

    count_messages_per_physical_port = FUNCTIONAL_CLASS.COUNT_MESSAGES_PER_PHYSICALPORT( messages_info )
    messages_per_physical_port = count_messages_per_physical_port.count_messages( physical_ports_information, physical_ports_index, physical_ports_index_reversed, physical_ports_adjacent_matrix )

    print( "length of messages_per_physical_port:", len( messages_per_physical_port ) ) #传输消息的A664端口数目
    records = [ [i, 0] for i in range(173) ]
    NUMBER_OF_MESSAGES = 0
    for item in list( messages_per_physical_port.keys() ):
        print(messages_per_physical_port[item])
        records[ len( messages_per_physical_port[item][1] ) ][1] += 1
        NUMBER_OF_MESSAGES += len( messages_per_physical_port[item][1] )
    print( "records:", records )
    print( "NUMBER_OF_MESSAGES:", NUMBER_OF_MESSAGES ) #messages_info中的消息不区分A、B端口，而messages_per_physical_port中的消息是区分A、B端口计算的，所以数目有所增加（这里可以检验一下，数目是否对的上？！）

    generate_files_for_routing = FUNCTIONAL_CLASS.GENERATE_FILES_FOR_ROUTING( arinc664_physical_ports_adjacent_matrix_for_A_NET, arinc664_physical_ports_adjacent_matrix_for_B_NET, switches_information, messages_info )
    generate_files_for_routing.counting_connections_of_a_b_net()
    generate_files_for_routing.save_connections_of_afdx()
    generate_files_for_routing.save_messages_of_afdx()

    save_intermediate_file = FUNCTIONAL_CLASS.SAVE_INTERMEDIATE_FILE()
    save_intermediate_file.save_file(
        physical_ports_information,
        physical_ports_adjacent_matrix,
        physical_ports_index,
        physical_ports_index_reversed,
        switches_information,
        RDIU_information,
        messages_info
    )