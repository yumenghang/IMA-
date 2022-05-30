import OPTIMIZATION_MODEL
class MESSAGES_PREPROCESSED():
    def messages_preprocessed( self, messages_of_physical_port, physical_ports_information, VL_DICT_OF_A_NET, VL_DICT_OF_B_NET, GAP, TIMELIMITED ):
        if messages_of_physical_port[0] in [ "RDIU_01", "RDIU_02", "RDIU_03", "RDIU_04", "RDIU_05", "RDIU_06", "RDIU_07", "RDIU_08", "RDIU_09", "RDIU_10", "RDIU_11", "RDIU_12", "RDIU_13", "RDIU_14", "RDIU_15", "RDIU_16"]:
            """
            首先判断目的物理端口的类型：ARINC664或非ARINC664
            若目的物理端口类型为ARINC664，则进一步判断是A网端口还是B网端口；
            1、若目的物理端口类型为ARINC664且为A网端口，或者目的物理端口为非ARINC664，则将消息划分进A网的虚链路中
            2、若目的物理端口类型为ARINC664且为B网端口，则将消息划分进B网的虚链路中
            """
            for MESSAGE_TYPE in ["CAN", "A429", "Analog"]:
                for NET_TYPE in ["A", "B"]:
                    locals()[ MESSAGE_TYPE + "_SIZE_OF_" + NET_TYPE + "_NET" ] = []
                    locals()[ MESSAGE_TYPE + "_DELAY_OF_" + NET_TYPE + "_NET" ] = []
                    locals()[ MESSAGE_TYPE + "_PERIOD_OF_" + NET_TYPE + "_NET" ] = []
                    locals()[ MESSAGE_TYPE + "_DICT_OF_" + NET_TYPE + "_NET" ] = dict()
                    locals()[ MESSAGE_TYPE + "_INDEX_OF_" + NET_TYPE + "_NET" ] = 0
                    locals()[ MESSAGE_TYPE + "_MESSAGES_GUID_OF_" + NET_TYPE + "_NET" ] = []
                    locals()[ MESSAGE_TYPE + "_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ] = []
                    locals()[ MESSAGE_TYPE + "_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ] = []
            for Non_ARINC664_messages_index in range( len( messages_of_physical_port[1] ) ):
                message_type = messages_of_physical_port[1][Non_ARINC664_messages_index]
                INDICATOR_OF_A_NET, INDICATOR_OF_B_NET = 1, 1
                for MESSAGE_TYPE in ["CAN", "A429", "Analog"]:
                    for NET_TYPE in ["A", "B"]:
                        locals()[ MESSAGE_TYPE + "_logical_destination_of_" + NET_TYPE + "_NET" ], locals()[ MESSAGE_TYPE + "_physical_destination_of_" + NET_TYPE + "_NET" ] = [], []
                for logical_port_index in range( len( messages_of_physical_port[6][Non_ARINC664_messages_index] ) ): # len( messages_of_physical_port[6][Non_ARINC664_messages_index] )表示该消息被发送至逻辑端口的数目
                    for physical_port_index in range( len( messages_of_physical_port[7][Non_ARINC664_messages_index][logical_port_index] ) ): # 发送至同一个逻辑端口的消息可能途径A、B网的两个物理端口
                        physical_port_name = messages_of_physical_port[7][Non_ARINC664_messages_index][logical_port_index][physical_port_index]
                        if physical_ports_information[ physical_port_name ][0] == "AswPhysPort" or physical_ports_information[ physical_port_name ][0] == "AesPhysPort":
                            if physical_port_name[-2:] == ".A":
                                if INDICATOR_OF_A_NET == 1:
                                    locals()[ message_type + "_SIZE_OF_A_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_DELAY_OF_A_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_PERIOD_OF_A_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ])
                                    locals()[ message_type + "_DICT_OF_A_NET"][ locals()[ message_type + "_INDEX_OF_A_NET" ] ] = Non_ARINC664_messages_index
                                    locals()[ message_type + "_INDEX_OF_A_NET" ] += 1
                                    locals()[ message_type + "_MESSAGES_GUID_OF_A_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                    INDICATOR_OF_A_NET = 0
                                locals()[ message_type + "_logical_destination_of_A_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                                locals()[ message_type + "_physical_destination_of_A_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                            else:
                                if INDICATOR_OF_B_NET == 1:
                                    locals()[ message_type + "_SIZE_OF_B_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_DELAY_OF_B_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_PERIOD_OF_B_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ])
                                    locals()[ message_type + "_DICT_OF_B_NET"][ locals()[ message_type + "_INDEX_OF_B_NET" ] ] = Non_ARINC664_messages_index
                                    locals()[ message_type + "_INDEX_OF_B_NET" ] += 1
                                    locals()[ message_type + "_MESSAGES_GUID_OF_B_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                    INDICATOR_OF_B_NET = 0
                                locals()[ message_type + "_logical_destination_of_B_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                                locals()[ message_type + "_physical_destination_of_B_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                        else:
                            if INDICATOR_OF_A_NET == 1:
                                locals()[ message_type + "_SIZE_OF_A_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_DELAY_OF_A_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_PERIOD_OF_A_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_DICT_OF_A_NET" ][ locals()[ message_type + "_INDEX_OF_A_NET"]] = Non_ARINC664_messages_index
                                locals()[ message_type + "_INDEX_OF_A_NET" ] += 1
                                locals()[ message_type + "_MESSAGES_GUID_OF_A_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                INDICATOR_OF_A_NET = 0
                            locals()[ message_type + "_logical_destination_of_A_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                            locals()[ message_type + "_physical_destination_of_A_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                for NET_TYPE in ["A", "B"]:
                    if locals()[ message_type + "_logical_destination_of_" + NET_TYPE + "_NET" ] != []:
                        locals()[ message_type + "_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ].append( locals()[ message_type + "_logical_destination_of_" + NET_TYPE + "_NET" ] )
                        locals()[ message_type + "_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ].append( locals()[ message_type + "_physical_destination_of_" + NET_TYPE + "_NET" ] )

            for MESSAGE_TYPE in ["CAN", "A429", "Analog"]:
                for NET_TYPE in ["A", "B"]:
                    INFORMATION = [ locals()[ MESSAGE_TYPE + "_SIZE_OF_" + NET_TYPE + "_NET" ],
                                    locals()[ MESSAGE_TYPE + "_DELAY_OF_" + NET_TYPE + "_NET" ],
                                    locals()[ MESSAGE_TYPE + "_PERIOD_OF_" + NET_TYPE + "_NET" ],
                                    locals()[ MESSAGE_TYPE + "_MESSAGES_GUID_OF_" + NET_TYPE + "_NET" ],
                                    locals()[ MESSAGE_TYPE + "_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ],
                                    locals()[ MESSAGE_TYPE + "_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ]
                                    ]
                    vl_of_rdiu_and_system = OPTIMIZATION_MODEL.VL_OF_RDIU_AND_END_SYSTEM( INFORMATION )
                    PHYSICAL_PORT_RATE = physical_ports_information[ messages_of_physical_port[0] + "." + NET_TYPE ][7] * 1000
                    try:
                        locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] = vl_of_rdiu_and_system.vl_of_rdiu_with_period( GAP, 2*TIMELIMITED, PHYSICAL_PORT_RATE )
                    except AttributeError:
                        locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] = vl_of_rdiu_and_system.vl_of_rdiu_no_period( GAP, 2*TIMELIMITED, PHYSICAL_PORT_RATE )
                    if NET_TYPE == "A":
                        if messages_of_physical_port[0] + ".A" in VL_DICT_OF_A_NET:
                            VL_DICT_OF_A_NET[ messages_of_physical_port[0] + ".A" ] += locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                        else:
                            if locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] != []:
                                VL_DICT_OF_A_NET[ messages_of_physical_port[0] + ".A" ] = locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                    else:
                        if messages_of_physical_port[0] + ".B" in VL_DICT_OF_B_NET:
                            VL_DICT_OF_B_NET[ messages_of_physical_port[0] + ".B" ] += locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                        else:
                            if locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] != []:
                                VL_DICT_OF_B_NET[ messages_of_physical_port[0] + ".B" ] = locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]

            return [ VL_DICT_OF_A_NET, VL_DICT_OF_B_NET]
        else:
            """
            首先判断目的物理端口的类型：ARINC664或非ARINC664
            若目的物理端口类型为ARINC664，则进一步判断是A网端口还是B网端口；
            1、若目的物理端口类型为ARINC664且为A网端口，或者目的物理端口为非ARINC664，则将消息划分进A网的虚链路中
            2、若目的物理端口类型为ARINC664且为B网端口，则将消息划分进B网的虚链路中
            """
            for NET_TYPE in ["A", "B"]:
                locals()[ "A664_SIZE_OF_" + NET_TYPE + "_NET" ] = []
                locals()[ "A664_DELAY_OF_" + NET_TYPE + "_NET" ] = []
                locals()[ "A664_PERIOD_OF_" + NET_TYPE + "_NET" ] = []
                locals()[ "A664_DICT_OF_" + NET_TYPE + "_NET" ] = dict()
                locals()[ "A664_INDEX_OF_" + NET_TYPE + "_NET" ] = 0
                locals()[ "A664_MESSAGES_GUID_OF_" + NET_TYPE + "_NET" ] = []
                locals()[ "A664_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ] = []
                locals()[ "A664_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ] = []
            for Non_ARINC664_messages_index in range( len( messages_of_physical_port[1] ) ):
                message_type = messages_of_physical_port[1][Non_ARINC664_messages_index] # A664
                if message_type != "A664":
                    print( "There is an error in message type!" )
                    break
                INDICATOR_OF_A_NET, INDICATOR_OF_B_NET = 1, 1
                for NET_TYPE in ["A", "B"]:
                    locals()[ "A664_logical_destination_of_" + NET_TYPE + "_NET" ], locals()[ "A664_physical_destination_of_" + NET_TYPE + "_NET" ] = [], []
                for logical_port_index in range( len( messages_of_physical_port[6][Non_ARINC664_messages_index] ) ): # len( messages_of_physical_port[6][Non_ARINC664_messages_index] )表示该消息被发送至逻辑端口的数目
                    for physical_port_index in range( len( messages_of_physical_port[7][Non_ARINC664_messages_index][logical_port_index] ) ): # 发送至同一个逻辑端口的消息可能途径A、B网的两个物理端口
                        physical_port_name = messages_of_physical_port[7][Non_ARINC664_messages_index][logical_port_index][physical_port_index]
                        if physical_ports_information[ physical_port_name ][0] == "AswPhysPort" or physical_ports_information[ physical_port_name ][0] == "AesPhysPort":
                            if physical_port_name[-2:] == ".A":
                                if INDICATOR_OF_A_NET == 1:
                                    locals()[ message_type + "_SIZE_OF_A_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_DELAY_OF_A_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_PERIOD_OF_A_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ])
                                    locals()[ message_type + "_DICT_OF_A_NET"][ locals()[ message_type + "_INDEX_OF_A_NET" ] ] = Non_ARINC664_messages_index
                                    locals()[ message_type + "_INDEX_OF_A_NET" ] += 1
                                    locals()[ message_type + "_MESSAGES_GUID_OF_A_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                    INDICATOR_OF_A_NET = 0
                                locals()[ message_type + "_logical_destination_of_A_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                                locals()[ message_type + "_physical_destination_of_A_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                            else:
                                if INDICATOR_OF_B_NET == 1:
                                    locals()[ message_type + "_SIZE_OF_B_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_DELAY_OF_B_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                    locals()[ message_type + "_PERIOD_OF_B_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ])
                                    locals()[ message_type + "_DICT_OF_B_NET"][ locals()[ message_type + "_INDEX_OF_B_NET" ] ] = Non_ARINC664_messages_index
                                    locals()[ message_type + "_INDEX_OF_B_NET" ] += 1
                                    locals()[ message_type + "_MESSAGES_GUID_OF_B_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                    INDICATOR_OF_B_NET = 0
                                locals()[ message_type + "_logical_destination_of_B_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                                locals()[ message_type + "_physical_destination_of_B_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                        else:
                            if INDICATOR_OF_A_NET == 1:
                                locals()[ message_type + "_SIZE_OF_A_NET" ].append( messages_of_physical_port[2][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_DELAY_OF_A_NET" ].append( messages_of_physical_port[3][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_PERIOD_OF_A_NET" ].append( messages_of_physical_port[4][ Non_ARINC664_messages_index ] )
                                locals()[ message_type + "_DICT_OF_A_NET" ][ locals()[ message_type + "_INDEX_OF_A_NET"]] = Non_ARINC664_messages_index
                                locals()[ message_type + "_INDEX_OF_A_NET" ] += 1
                                locals()[ message_type + "_MESSAGES_GUID_OF_A_NET" ].append( messages_of_physical_port[5][ Non_ARINC664_messages_index ] )
                                INDICATOR_OF_A_NET = 0
                            locals()[ message_type + "_logical_destination_of_A_NET" ].append( messages_of_physical_port[6][ Non_ARINC664_messages_index ][ logical_port_index ] )
                            locals()[ message_type + "_physical_destination_of_A_NET" ].append( messages_of_physical_port[7][ Non_ARINC664_messages_index ][ logical_port_index ][ physical_port_index ] )
                for NET_TYPE in ["A", "B"]:
                    if locals()[ message_type + "_logical_destination_of_" + NET_TYPE + "_NET" ] != []:
                        locals()[ message_type + "_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ].append( locals()[ message_type + "_logical_destination_of_" + NET_TYPE + "_NET" ] )
                        locals()[ message_type + "_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ].append( locals()[ message_type + "_physical_destination_of_" + NET_TYPE + "_NET" ] )

            for NET_TYPE in ["A", "B"]:
                INFORMATION = [ locals()[ "A664_SIZE_OF_" + NET_TYPE + "_NET" ],
                                locals()[ "A664_DELAY_OF_" + NET_TYPE + "_NET" ],
                                locals()[ "A664_PERIOD_OF_" + NET_TYPE + "_NET" ],
                                locals()[ "A664_MESSAGES_GUID_OF_" + NET_TYPE + "_NET" ],
                                locals()[ "A664_LOGICAL_DESTINATION_OF_" + NET_TYPE + "_NET" ],
                                locals()[ "A664_PHYSICAL_PORT_OF_" + NET_TYPE + "_NET" ]
                                ]
                vl_of_rdiu_and_end_system = OPTIMIZATION_MODEL.VL_OF_RDIU_AND_END_SYSTEM( INFORMATION )
                PHYSICAL_PORT_RATE = physical_ports_information[ messages_of_physical_port[0] ][7] * 1000
                timelimited = int( len( messages_of_physical_port[1] ) / 10 ) * TIMELIMITED
                locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] = vl_of_rdiu_and_end_system.vl_of_end_system( GAP, timelimited, PHYSICAL_PORT_RATE )
                if NET_TYPE == "A":
                    if messages_of_physical_port[0] + ".A" in VL_DICT_OF_A_NET:
                        VL_DICT_OF_A_NET[ messages_of_physical_port[0] ] += locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                    else:
                        if locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] != []:
                            VL_DICT_OF_A_NET[ messages_of_physical_port[0] ] = locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                else:
                    if messages_of_physical_port[0] + ".B" in VL_DICT_OF_B_NET:
                        VL_DICT_OF_B_NET[ messages_of_physical_port[0] ] += locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]
                    else:
                        if locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ] != []:
                            VL_DICT_OF_B_NET[ messages_of_physical_port[0] ] = locals()[ "VL_INFORMATION_OF_" + NET_TYPE + "_NET" ]

            return [ VL_DICT_OF_A_NET, VL_DICT_OF_B_NET]