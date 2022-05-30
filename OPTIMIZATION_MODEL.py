import numpy as np
from gurobipy import *

HEAD_OF_FRAME = 47  # 虚链路帧头大小
MINIMUM_FRAME = 17  # 最小帧长（不包括帧头）
MAXIMUM_FRAME = 1471  # 最大帧长（不包括帧头）
LATENCY_LIMITED_FRACTION = 1/2 # 表示以系统对消息时延要求的LATENCY_LIMITED_FRACTION作为消息除路由外的时间限制
NUMBER_OF_SUB_VIRTUAL_LINKS = 4 # 每条虚链路内最多有4条子虚拟链路
MAX = sys.maxsize

class VL_OF_RDIU_AND_END_SYSTEM():
    def __init__(self, INFORMATION):
        self.SIZE_OF_MESSAGE = INFORMATION[0]
        self.DELAY_BOUND_OF_MESSAGE = INFORMATION[1]
        self.PERIOD_OF_MESSAGE = INFORMATION[2]
        self.GUID_OF_MESSAGE = INFORMATION[3]
        self.LOGICAL_DESTINATION_OF_MESSAGE = INFORMATION[4]
        self.PHYSICAL_DESTINATION_OF_MESSAGE = INFORMATION[5]
        print("Number of messages:", len(self.SIZE_OF_MESSAGE))
        print("SIZE_OF_MESSAGE", self.SIZE_OF_MESSAGE)
        print("DELAY_BOUND_OF_MESSAGE", self.DELAY_BOUND_OF_MESSAGE)
        print("PERIOD_OF_MESSAGE", self.PERIOD_OF_MESSAGE)
        print("self.LOGICAL_DESTINATION_OF_MESSAGE:", self.LOGICAL_DESTINATION_OF_MESSAGE)
        print("self.PHYSICAL_DESTINATION_OF_MESSAGE:", self.PHYSICAL_DESTINATION_OF_MESSAGE)
        print("self.LOGICAL_DESTINATION_OF_MESSAGE:", len(self.LOGICAL_DESTINATION_OF_MESSAGE))

    def vl_of_rdiu_with_period(self, GAP, TIMELIMITED, PHYSICAL_PORT_RATE):
        NUMBER_OF_MESSAGES = len(self.SIZE_OF_MESSAGE)  # 消息的数目

        md = Model("Integer Linear Programming")

        VIRTUAL_LINKS = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="VIRTUAL_LINKS" )  # 一维数组：长度为NUMBER_OF_MESSAGES，记录虚链路的分布。取值为0或1，当取值为1时，表示有此条虚拟链路；取值为0时，表示无此条虚拟链路
        BELONG = md.addVars( NUMBER_OF_MESSAGES, NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="BELONG" )  # 消息message_index与虚拟链路VL的对应关系，前一个NUMBER_OF_MESSAGES表示消息，后一个NUMBER_OF_MESSAGES表示虚链路，综合表示一条消息是否属于虚链路

        # 一维数组，记录：每一条虚链路VL的切片数目。注意，这里虚链路的切片数目满足：(NUM-1)*MTU <SIZE <= NUM*MTU，即：确定了NUMBER_OF_FRAMES_OF_VL的上、下确界（注：SIZE表示所有属于此虚链路的消息的大小之和）
        NUMBER_OF_FRAMES_OF_VL = md.addVars( NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_VL" )
        # 一维数组，记录：每条消息的切片数目。注意，这里消息的切片数目满足：(num-1)*MTU < size <= num*MTU，即：确定了number_of_frames_of_message的上、下确界（注：size表示所有属于此消息的大小）
        NUMBER_OF_FRAMES_OF_MESSAGES = md.addVars( NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_MESSAGES" )
        FRAME_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_VL" )  # 记录每一条虚链路VL的MTU大小
        FRAME_SIZE_OF_MESSAGES = md.addVars( NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_MESSAGES" )  # 记录每一条消息的MTU大小，其大小等于该消息所属的虚链路的MTU大小
        FREQUENCE_OF_MESSAGES = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="FREQUENCE_OF_MESSAGES" )  # 一维数组，记录：每一条消息单位时间内切片的数目

        SIZE_OF_TRANSMITTED_IN_BAG = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="SIZE_OF_TRANSMITTED_IN_BAG" )  # BAG时间内，物理端口最多可以发送的消息大小+该虚拟链路的一个切片大小
        SIZE_OF_ALL_EXISTING_VL = md.addVar( lb=MINIMUM_FRAME, name="SIZE_OF_ALL_EXISTING_VL" )  # 所有真实存在的虚链路的一个MTU之和

        UPPER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_VL" )  # 一维数组，记录：每一条虚链路的：NUMBER_OF_FRAMES_OF_VL*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的上确界
        LOWER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="LOWER_BOUND_OF_TOTAL_SIZE_OF_VL" )  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_VL-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的下确界
        UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES" )  # 一维数组，记录：每一条消息的：NUMBER_OF_FRAMES_OF_MESSAGES*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的上确界

        VALUE_OF_K = md.addVars( NUMBER_OF_MESSAGES, lb=1, ub=2048, vtype=GRB.INTEGER, name="VALUE_OF_K" )  # 一维数组，记录：每一条虚拟链路VL的BAG的参数
        VALUE_OF_BAG = md.addVars( NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="VALUE_OF_BAG" )  # 一维数组，记录：每一条虚拟链路VL的BAG的大小
        RECIPROCAL_OF_BAG = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="RECIPROCAL_OF_BAG" )  # 一维数组，记录：每一条虚拟链路VL的BAG的倒数
        CYCLE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="CYCLE_OF_VL" )  # 一维数组，记录：每一条虚链路的BAG之和，大小等于：NUMBER_OF_FRAMES_OF_VL * VALUE_OF_BAG

        BANDWIDTH_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_VL" )  # 一维数组，记录：每一条虚拟链路VL的带宽
        BANDWIDTH_OF_EXISTING_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_EXISTING_VL" )  # 一维数组，记录：真实存在的虚拟链路VL的带宽占用，其值等于：BANDWIDTH_OF_VL*VIRTUAL_LINKS（注：这里的真实存在表示VIRTUAL_LINKS数组中对应取值为1）

        # 约束：一条消息只能同时属于一条虚拟链路
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( quicksum( BELONG[ message_index, virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) == 1 )
        # 约束：所有消息都必须有属于的一条虚拟链路VL
        # 约束：结合上一条约束，达到约束效果：所有消息都必须属于且仅能属于一条真实存在的虚拟链路VL
        md.addConstr( quicksum( quicksum( BELONG[ message_index, virtual_link_index ] * VIRTUAL_LINKS[ virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) for message_index in range( NUMBER_OF_MESSAGES ) ) == NUMBER_OF_MESSAGES )
        # 约束：BELONG数组中，某一列（对应某一虚拟链路VL）中元素全为0时，表示没有消息属于此虚拟链路，因此该条虚拟链路不应该存在，所以限制其值必须取为0
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( VIRTUAL_LINKS[ virtual_link_index ] <= quicksum( BELONG[ message_index, virtual_link_index ] for message_index in range( NUMBER_OF_MESSAGES ) ) )

        # 约束：消息的帧大小等于该消息所属的虚拟链路的帧大小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( FRAME_SIZE_OF_MESSAGES[ message_index ] == quicksum( FRAME_SIZE_OF_VL[ virtual_link_index ] * BELONG[ message_index, virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) )

        # 约束：根据虚拟链路BAG参数的取值，确定BAG的大小和BAG的倒数
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( VALUE_OF_BAG[ virtual_link_index ] * 2 == VALUE_OF_K[ virtual_link_index ] )
            md.addConstr( VALUE_OF_BAG[ virtual_link_index ] * RECIPROCAL_OF_BAG[ virtual_link_index ] == 1 )

        # 约束：确定NUMBER_OF_FRAMES_OF_VL，既要保证足够大，能够把所有消息的内容传输完毕，也不能够太大
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == NUMBER_OF_FRAMES_OF_VL[virtual_link_index] * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr( LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == ( NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] >= quicksum( self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] <= quicksum( self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            # 各条虚链在RDIU内的时延为：( NUMBER_OF_FRAMES_OF_VL - 1 ) * BAG
            md.addConstr( CYCLE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * VALUE_OF_BAG[ virtual_link_index])
        # 约束：每一条消息的传输时延等于其所属的虚链路VL的传输时延，因此要约束其小于系统对此条消息的传输时延要求
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum( BELONG[message_index, virtual_link_index] * CYCLE_OF_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) <= self.DELAY_BOUND_OF_MESSAGE[message_index] * LATENCY_LIMITED_FRACTION)

        # 约束：每一条消息的切片数目既不可太大，也不可太小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES[message_index] == NUMBER_OF_FRAMES_OF_MESSAGES[message_index] * FRAME_SIZE_OF_MESSAGES[message_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES[message_index] >= self.SIZE_OF_MESSAGE[message_index])
            md.addConstr( FREQUENCE_OF_MESSAGES[message_index] == NUMBER_OF_FRAMES_OF_MESSAGES[message_index] / self.PERIOD_OF_MESSAGE[ message_index ] )
        # 约束：频率约束
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum( FREQUENCE_OF_MESSAGES[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)) <= RECIPROCAL_OF_BAG[virtual_link_index])

        # 约束：对于任意真实存在的虚链路，其一个BAG时间内，物理端口必须能够将其余真实存在的虚链路的一个消息切片转发出去，否则会造成拥塞
        md.addConstr(SIZE_OF_ALL_EXISTING_VL == quicksum( FRAME_SIZE_OF_VL[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))  # 所有真实存在的虚链路的一个消息切片的大小之和
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] == PHYSICAL_PORT_RATE * VALUE_OF_BAG[ virtual_link_index] + FRAME_SIZE_OF_VL[ virtual_link_index])  # 任意一虚链路的一个BAG时间内，物理端口可以传输的消息大小 再加 该虚链路的一个消息切片大小
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] >= VIRTUAL_LINKS[ virtual_link_index] * SIZE_OF_ALL_EXISTING_VL)

        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BANDWIDTH_OF_VL[virtual_link_index] == HEAD_OF_FRAME * RECIPROCAL_OF_BAG[virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index])
            md.addConstr( BANDWIDTH_OF_EXISTING_VL[virtual_link_index] == BANDWIDTH_OF_VL[virtual_link_index] * VIRTUAL_LINKS[ virtual_link_index])

        md.addConstr( quicksum( BANDWIDTH_OF_EXISTING_VL[ virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) <= PHYSICAL_PORT_RATE )

        md.setObjective( quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)), GRB.MINIMIZE)

        #md.setParam('OutputFlag', 0)
        md.Params.NonConvex = 2
        if GAP != None:
            md.Params.MIPGap = GAP  # 设置求解混合整数规划的Gap为GAP
        if TIMELIMITED != None:
            md.Params.TimeLimit = TIMELIMITED  # 设置最长求解时间为 TIMELIMITED 秒
        md.optimize()

        virtual_links = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            virtual_links.append(VIRTUAL_LINKS[virtual_link_index].x)

        belong = []
        for message_index in range(NUMBER_OF_MESSAGES):
            intermediate = []
            for virtual_link_index in range(NUMBER_OF_MESSAGES):
                intermediate.append(int(BELONG[message_index, virtual_link_index].x))
            belong.append(intermediate)

        bag_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bag_of_vl.append(VALUE_OF_BAG[virtual_link_index].x)

        frame_size_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            frame_size_of_vl.append(FRAME_SIZE_OF_VL[virtual_link_index].x)

        bandwidth_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bandwidth_of_vl.append(BANDWIDTH_OF_VL[virtual_link_index].x)

        VL_INFORMATION = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            if virtual_links[ virtual_link_index ] == 1:
                vl_information = [ bag_of_vl[ virtual_link_index ], frame_size_of_vl[ virtual_link_index ], bandwidth_of_vl[ virtual_link_index ] ]
                messages_guid_of_sub_virtual_link, logical_destination_of_sub_virtual_link, physical_destination_of_sub_virtual_link = [], [], []
                for message_index in range( len( belong ) ):
                    if belong[ message_index ][ virtual_link_index ] == 1:
                        messages_guid_of_sub_virtual_link.append( self.GUID_OF_MESSAGE[ message_index ] )
                        logical_destination_of_sub_virtual_link += self.LOGICAL_DESTINATION_OF_MESSAGE[ message_index ]
                        physical_destination_of_sub_virtual_link +=  self.PHYSICAL_DESTINATION_OF_MESSAGE[ message_index ]
                # 因为RDIU内虚链路的优化问题，我们默认各条虚链路有且仅有一条子虚拟链路
                messages_guid = [ messages_guid_of_sub_virtual_link, [], [], [] ]
                logical_destination = [ logical_destination_of_sub_virtual_link, [], [], [] ]
                physical_destination = [ physical_destination_of_sub_virtual_link, [], [], [] ]
                vl_information.append( messages_guid )
                vl_information.append( logical_destination )
                vl_information.append( physical_destination )
                VL_INFORMATION.append( vl_information )
        return VL_INFORMATION

    def vl_of_rdiu_no_period(self, GAP, TIMELIMITED, PHYSICAL_PORT_RATE):
        NUMBER_OF_MESSAGES = len(self.SIZE_OF_MESSAGE)  # 消息的数目

        md = Model("Integer Linear Programming")

        VIRTUAL_LINKS = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="VIRTUAL_LINKS" )  # 一维数组：长度为NUMBER_OF_MESSAGES，记录虚链路的分布。取值为0或1，当取值为1时，表示有此条虚拟链路；取值为0时，表示无此条虚拟链路
        BELONG = md.addVars( NUMBER_OF_MESSAGES, NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="BELONG" )  # 消息message_index与虚拟链路VL的对应关系，前一个NUMBER_OF_MESSAGES表示消息，后一个NUMBER_OF_MESSAGES表示虚链路，综合表示一条消息是否属于虚链路

        # 一维数组，记录：每一条虚链路VL的切片数目。注意，这里虚链路的切片数目满足：(NUM-1)*MTU <SIZE <= NUM*MTU，即：确定了NUMBER_OF_FRAMES_OF_VL的上、下确界（注：SIZE表示所有属于此虚链路的消息的大小之和）
        NUMBER_OF_FRAMES_OF_VL = md.addVars( NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_VL" )
        FRAME_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_VL" )  # 记录每一条虚链路VL的MTU大小
        FRAME_SIZE_OF_MESSAGES = md.addVars( NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_MESSAGES" )  # 记录每一条消息的MTU大小，其大小等于该消息所属的虚链路的MTU大小

        SIZE_OF_TRANSMITTED_IN_BAG = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="SIZE_OF_TRANSMITTED_IN_BAG" )  # BAG时间内，物理端口最多可以发送的消息大小+该虚拟链路的一个切片大小
        SIZE_OF_ALL_EXISTING_VL = md.addVar( lb=MINIMUM_FRAME, name="SIZE_OF_ALL_EXISTING_VL" )  # 所有真实存在的虚链路的一个MTU之和

        UPPER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_VL" )  # 一维数组，记录：每一条虚链路的：NUMBER_OF_FRAMES_OF_VL*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的上确界
        LOWER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="LOWER_BOUND_OF_TOTAL_SIZE_OF_VL" )  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_VL-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的下确界

        VALUE_OF_K = md.addVars( NUMBER_OF_MESSAGES, lb=1, ub=2048, vtype=GRB.INTEGER, name="VALUE_OF_K" )  # 一维数组，记录：每一条虚拟链路VL的BAG的参数
        VALUE_OF_BAG = md.addVars( NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="VALUE_OF_BAG" )  # 一维数组，记录：每一条虚拟链路VL的BAG的大小
        RECIPROCAL_OF_BAG = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="RECIPROCAL_OF_BAG" )  # 一维数组，记录：每一条虚拟链路VL的BAG的倒数
        CYCLE_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="CYCLE_OF_VL" )  # 一维数组，记录：每一条虚链路的BAG之和，大小等于：NUMBER_OF_FRAMES_OF_VL * VALUE_OF_BAG

        BANDWIDTH_OF_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_VL" )  # 一维数组，记录：每一条虚拟链路VL的带宽
        BANDWIDTH_OF_EXISTING_VL = md.addVars( NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_EXISTING_VL" )  # 一维数组，记录：真实存在的虚拟链路VL的带宽占用，其值等于：BANDWIDTH_OF_VL*VIRTUAL_LINKS（注：这里的真实存在表示VIRTUAL_LINKS数组中对应取值为1）

        # 约束：一条消息只能同时属于一条虚拟链路
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( quicksum( BELONG[ message_index, virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) == 1 )
        # 约束：所有消息都必须有属于的一条虚拟链路VL
        # 约束：结合上一条约束，达到约束效果：所有消息都必须属于且仅能属于一条真实存在的虚拟链路VL
        md.addConstr( quicksum( quicksum( BELONG[ message_index, virtual_link_index ] * VIRTUAL_LINKS[ virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) for message_index in range( NUMBER_OF_MESSAGES ) ) == NUMBER_OF_MESSAGES )
        # 约束：BELONG数组中，某一列（对应某一虚拟链路VL）中元素全为0时，表示没有消息属于此虚拟链路，因此该条虚拟链路不应该存在，所以限制其值必须取为0
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( VIRTUAL_LINKS[ virtual_link_index ] <= quicksum( BELONG[ message_index, virtual_link_index ] for message_index in range( NUMBER_OF_MESSAGES ) ) )

        # 约束：消息的帧大小等于该消息所属的虚拟链路的帧大小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( FRAME_SIZE_OF_MESSAGES[ message_index ] == quicksum( FRAME_SIZE_OF_VL[ virtual_link_index ] * BELONG[ message_index, virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) )

        # 约束：根据虚拟链路BAG参数的取值，确定BAG的大小和BAG的倒数
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( VALUE_OF_BAG[ virtual_link_index ] * 2 == VALUE_OF_K[ virtual_link_index ] )
            md.addConstr( VALUE_OF_BAG[ virtual_link_index ] * RECIPROCAL_OF_BAG[ virtual_link_index ] == 1 )

        # 约束：确定NUMBER_OF_FRAMES_OF_VL，既要保证足够大，能够把所有消息的内容传输完毕，也不能够太大
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == NUMBER_OF_FRAMES_OF_VL[virtual_link_index] * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr( LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == ( NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] >= quicksum( self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] <= quicksum( self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            # 各条虚链在RDIU内的时延为：( NUMBER_OF_FRAMES_OF_VL - 1 ) * BAG
            md.addConstr( CYCLE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * VALUE_OF_BAG[ virtual_link_index])
        # 约束：每一条消息的传输时延等于其所属的虚链路VL的传输时延，因此要约束其小于系统对此条消息的传输时延要求
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum( BELONG[message_index, virtual_link_index] * CYCLE_OF_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) <= self.DELAY_BOUND_OF_MESSAGE[message_index] * LATENCY_LIMITED_FRACTION)

        # 约束：对于任意真实存在的虚链路，其一个BAG时间内，物理端口必须能够将其余真实存在的虚链路的一个消息切片转发出去，否则会造成拥塞
        md.addConstr(SIZE_OF_ALL_EXISTING_VL == quicksum( FRAME_SIZE_OF_VL[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))  # 所有真实存在的虚链路的一个消息切片的大小之和
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] == PHYSICAL_PORT_RATE * VALUE_OF_BAG[ virtual_link_index] + FRAME_SIZE_OF_VL[ virtual_link_index])  # 任意一虚链路的一个BAG时间内，物理端口可以传输的消息大小 再加 该虚链路的一个消息切片大小
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] >= VIRTUAL_LINKS[ virtual_link_index] * SIZE_OF_ALL_EXISTING_VL)

        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BANDWIDTH_OF_VL[virtual_link_index] == HEAD_OF_FRAME * RECIPROCAL_OF_BAG[virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index])
            md.addConstr( BANDWIDTH_OF_EXISTING_VL[virtual_link_index] == BANDWIDTH_OF_VL[virtual_link_index] * VIRTUAL_LINKS[ virtual_link_index])

        md.addConstr( quicksum( BANDWIDTH_OF_EXISTING_VL[ virtual_link_index ] for virtual_link_index in range( NUMBER_OF_MESSAGES ) ) <= PHYSICAL_PORT_RATE )

        md.setObjective( quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)), GRB.MINIMIZE)

        #md.setParam('OutputFlag', 0)
        md.Params.NonConvex = 2
        if GAP != None:
            md.Params.MIPGap = GAP  # 设置求解混合整数规划的Gap为GAP
        if TIMELIMITED != None:
            md.Params.TimeLimit = TIMELIMITED  # 设置最长求解时间为 TIMELIMITED 秒
        md.optimize()

        virtual_links = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            virtual_links.append(VIRTUAL_LINKS[virtual_link_index].x)

        belong = []
        for message_index in range(NUMBER_OF_MESSAGES):
            intermediate = []
            for virtual_link_index in range(NUMBER_OF_MESSAGES):
                intermediate.append(int(BELONG[message_index, virtual_link_index].x))
            belong.append(intermediate)

        bag_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bag_of_vl.append(VALUE_OF_BAG[virtual_link_index].x)

        frame_size_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            frame_size_of_vl.append(FRAME_SIZE_OF_VL[virtual_link_index].x)

        bandwidth_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bandwidth_of_vl.append(BANDWIDTH_OF_VL[virtual_link_index].x)

        VL_INFORMATION = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            if virtual_links[ virtual_link_index ] == 1:
                vl_information = [ bag_of_vl[ virtual_link_index ], frame_size_of_vl[ virtual_link_index ], bandwidth_of_vl[ virtual_link_index ] ]
                messages_guid_of_sub_virtual_link, logical_destination_of_sub_virtual_link, physical_destination_of_sub_virtual_link = [], [], []
                for message_index in range( len( belong ) ):
                    if belong[ message_index ][ virtual_link_index ] == 1:
                        messages_guid_of_sub_virtual_link.append( self.GUID_OF_MESSAGE[ message_index ] )
                        logical_destination_of_sub_virtual_link += self.LOGICAL_DESTINATION_OF_MESSAGE[ message_index ]
                        physical_destination_of_sub_virtual_link +=  self.PHYSICAL_DESTINATION_OF_MESSAGE[ message_index ]
                # 因为RDIU内虚链路的优化问题，我们默认各条虚链路有且仅有一条子虚拟链路
                messages_guid = [ messages_guid_of_sub_virtual_link, [], [], [] ]
                logical_destination = [ logical_destination_of_sub_virtual_link, [], [], [] ]
                physical_destination = [ physical_destination_of_sub_virtual_link, [], [], [] ]
                vl_information.append( messages_guid )
                vl_information.append( logical_destination )
                vl_information.append( physical_destination )
                VL_INFORMATION.append( vl_information )
        return VL_INFORMATION

    def vl_of_end_system(self, GAP, TIMELIMITED, PHYSICAL_PORT_RATE):
        NUMBER_OF_MESSAGES = len(self.SIZE_OF_MESSAGE)  # 消息的数目，子虚拟链路的数目

        md = Model("Integer Linear Programming")

        VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="VIRTUAL_LINKS")  # 一维数组：长度为NUMBER_OF_MESSAGES，记录虚链路的分布。取值为0或1，当取值为1时，表示有此条虚拟链路；取值为0时，表示无此条虚拟链路
        SUB_VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_SUB_VIRTUAL_LINKS, vtype=GRB.BINARY, name="SUB_VIRTUAL_LINKS")  # 二维数组：大小为NUMBER_OF_MESSAGES * NUMBER_OF_SUB_VIRTUAL_LINKS，记录各条虚链路的子虚拟链路分布。取值为0或1，当取值为1时，表示有此条子虚拟链路；取值为0时，表示无此条子虚拟链路
        BELONG = {}
        # BELONG: 字典，记录消息message_index与虚拟链路virtual_link_index以及相应的子虚拟链路sub_virtual_link_index的对应关系
        # 综合表示一条消息是否属于虚链路
        for message_index in range(NUMBER_OF_MESSAGES):
            for virtual_link_index in range(NUMBER_OF_MESSAGES):
                for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                    BELONG[message_index, virtual_link_index, sub_virtual_link_index] = md.addVar(vtype=GRB.BINARY, name="BELONG_" + str( message_index) + "_" + str( virtual_link_index) + "_" + str( sub_virtual_link_index))

        # 一维数组，记录：每条消息的切片数目。注意，这里消息的切片数目满足：(num-1)*MTU < size <= num*MTU，即：确定了number_of_frames_of_message的上、下确界（注：size表示所有属于此消息的大小）
        NUMBER_OF_FRAMES_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_MESSAGES")
        FRAME_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_VL")  # 记录每一条虚链路VL的MTU大小
        FRAME_SIZE_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_MESSAGES")  # 记录每一条消息的MTU大小，其大小等于该消息所属的虚链路的MTU大小
        BAG_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="BAG_OF_MESSAGES")  # 一维数组，记录：每一条消息的BAG的大小
        FREQUENCE_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="FREQUENCE_OF_MESSAGES")  # 一维数组，记录：每一条消息单位时间内切片的数目

        NUMBER_OF_SUB_VIRTUAL_LINKS_OF_VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, lb=0, ub=4, vtype=GRB.INTEGER, name="NUMBER_OF_SUB_VIRTUAL_LINKS_OF_VIRTUAL_LINKS")  # 一维数组，记录：每一条虚拟链路中子虚拟链路的数目
        NUMBER_OF_MESSAGES_PER_SUB_VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_SUB_VIRTUAL_LINKS, lb=0, ub=NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="NUMBER_OF_MESSAGES_PER_SUB_VIRTUAL_LINKS")  # 二维数组：大小为NUMBER_OF_MESSAGES * NUMBER_OF_SUB_VIRTUAL_LINKS，记录各条虚链路中子虚拟链路上消息的数目
        TRUE_NUMBER_OF_BAG_OF_SUB_VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_SUB_VIRTUAL_LINKS, vtype=GRB.CONTINUOUS, name="TRUE_NUMBER_OF_BAG_OF_SUB_VIRTUAL_LINKS")  # 二维数组，记录：每一条虚拟链路VL中子虚拟链路的真实BAG的数目，所谓真实BAG的数目，是指在物理链路上转发时，受物理端口轮询式转发方式的影响，同一消息的前后两个切片之间的真实BAG的数目
        TRUE_BAG_OF_SUB_VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_SUB_VIRTUAL_LINKS, vtype=GRB.CONTINUOUS, name="TRUE_BAG_OF_SUB_VIRTUAL_LINKS")  # 二维数组，记录：每一条虚拟链路VL中子虚拟链路的真实BAG，所谓真实BAG，是指：真实BAG的数目*该虚拟链路的BAG大小

        SIZE_OF_TRANSMITTED_IN_BAG = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="SIZE_OF_TRANSMITTED_IN_BAG")  # BAG时间内，物理端口最多可以发送的消息大小
        SIZE_OF_ALL_EXISTING_VL = md.addVar(lb=MINIMUM_FRAME, name="SIZE_OF_ALL_EXISTING_VL")  # 所有真实存在的虚链路的一个MTU之和

        UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES")  # 一维数组，记录：每一条消息的：NUMBER_OF_FRAMES_OF_MESSAGES*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的上确界

        VALUE_OF_K = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=2048, vtype=GRB.INTEGER, name="VALUE_OF_K")  # 一维数组，记录：每一条虚拟链路VL的BAG的参数
        VALUE_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="VALUE_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的大小
        RECIPROCAL_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="RECIPROCAL_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的倒数

        BANDWIDTH_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_VL")  # 一维数组，记录：每一条虚拟链路VL的带宽
        BANDWIDTH_OF_EXISTING_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_EXISTING_VL")  # 一维数组，记录：真实存在的虚拟链路VL的带宽占用，其值等于：BANDWIDTH_OF_VL*VIRTUAL_LINKS（注：这里的真实存在表示VIRTUAL_LINKS数组中对应取值为1）

        # 约束：一条消息只能同时属于一条虚拟链路VL、一条子虚拟链路subVL
        # 约束：所有消息都必须有属于的一条虚拟链路VL、一条子虚拟链路subVL
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for virtual_link_index in range(NUMBER_OF_MESSAGES)) == 1)
        # 约束：结合上一条约束，达到约束效果：
        # 所有消息都必须属于且仅能属于一条真实存在的虚拟链路VL
        # 所有消息都必须属于且仅能属于一条真实存在的子虚拟链路subVL
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] * SUB_VIRTUAL_LINKS[ virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for virtual_link_index in range(NUMBER_OF_MESSAGES)) == 1)
            md.addConstr(quicksum(quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) == 1)

        # 约束：BELONG数组中，
        # 某一列（对应某一虚拟链路VL）中元素全为0时，表示没有消息属于此虚拟链路，因此该条虚拟链路不应该存在，所以限制其值必须取为0
        # 某一列（对应某一子虚拟链路subVL）中元素全为0时，表示没有消息属于此子虚拟链路，因此该条子虚拟链路不应该存在，所以限制其值必须取为0
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VIRTUAL_LINKS[virtual_link_index] <= quicksum(quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for message_index in range(NUMBER_OF_MESSAGES)))
            for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                md.addConstr(SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] <= quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
        # 约束：消息的帧大小等于该消息所属的虚拟链路的帧大小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(FRAME_SIZE_OF_MESSAGES[message_index] == quicksum( FRAME_SIZE_OF_VL[virtual_link_index] * quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for virtual_link_index in range(NUMBER_OF_MESSAGES)))

        # 约束：根据虚拟链路BAG参数的取值，确定BAG的大小和BAG的倒数
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VALUE_OF_BAG[virtual_link_index] * 2 == VALUE_OF_K[virtual_link_index])
            md.addConstr(VALUE_OF_BAG[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index] == 1)

        # 约束：确定NUMBER_OF_FRAMES_OF_VL，既要保证足够大，能够把所有消息的内容传输完毕，也不能够太大
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES[message_index] == NUMBER_OF_FRAMES_OF_MESSAGES[message_index] * FRAME_SIZE_OF_MESSAGES[message_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_MESSAGES[message_index] >= self.SIZE_OF_MESSAGE[message_index])

        # 约束：每一条消息的传输时延等于其所属的虚链路VL的传输时延，因此要约束其小于系统对此条消息的传输时延要求
        # 因为消息在虚链路上以轮询的方式进行转发，因此，虚链路的真实BAG为虚链路的BAG*该虚链路上消息的数目
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(NUMBER_OF_SUB_VIRTUAL_LINKS_OF_VIRTUAL_LINKS[virtual_link_index] == quicksum( SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)))
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                md.addConstr( NUMBER_OF_MESSAGES_PER_SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] == quicksum( BELONG[message_index, virtual_link_index, sub_virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                md.addConstr(TRUE_NUMBER_OF_BAG_OF_SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] == NUMBER_OF_SUB_VIRTUAL_LINKS_OF_VIRTUAL_LINKS[virtual_link_index] * NUMBER_OF_MESSAGES_PER_SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index])
                md.addConstr(TRUE_BAG_OF_SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] == VALUE_OF_BAG[ virtual_link_index] * TRUE_NUMBER_OF_BAG_OF_SUB_VIRTUAL_LINKS[ virtual_link_index, sub_virtual_link_index])
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BAG_OF_MESSAGES[message_index] == quicksum(quicksum( TRUE_BAG_OF_SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index] * BELONG[ message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for virtual_link_index in range(NUMBER_OF_MESSAGES)))
            md.addConstr((NUMBER_OF_FRAMES_OF_MESSAGES[message_index] - 1) * BAG_OF_MESSAGES[message_index] <= self.DELAY_BOUND_OF_MESSAGE[message_index] * LATENCY_LIMITED_FRACTION)

        # 约束：对于任意真实存在的虚链路，其一个BAG时间内，物理端口必须能够将其余真实存在的虚链路的一个消息切片转发出去，否则会造成拥塞
        md.addConstr(SIZE_OF_ALL_EXISTING_VL == quicksum( FRAME_SIZE_OF_VL[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))  # 所有真实存在的虚链路的一个消息切片的大小之和
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] == PHYSICAL_PORT_RATE * VALUE_OF_BAG[ virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(SIZE_OF_TRANSMITTED_IN_BAG[virtual_link_index] >= VIRTUAL_LINKS[ virtual_link_index] * SIZE_OF_ALL_EXISTING_VL)

        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( FREQUENCE_OF_MESSAGES[message_index] == NUMBER_OF_FRAMES_OF_MESSAGES[message_index] / self.PERIOD_OF_MESSAGE[ message_index])
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(RECIPROCAL_OF_BAG[virtual_link_index] >= quicksum(quicksum( FREQUENCE_OF_MESSAGES[message_index] * BELONG[message_index, virtual_link_index, sub_virtual_link_index] for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS)) for message_index in range(NUMBER_OF_MESSAGES)))

        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BANDWIDTH_OF_VL[virtual_link_index] == HEAD_OF_FRAME * RECIPROCAL_OF_BAG[virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index])
            md.addConstr( BANDWIDTH_OF_EXISTING_VL[virtual_link_index] == BANDWIDTH_OF_VL[virtual_link_index] * VIRTUAL_LINKS[ virtual_link_index])

        md.addConstr(quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) <= PHYSICAL_PORT_RATE)

        md.setObjective( quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)), GRB.MINIMIZE)

        #md.setParam('OutputFlag', 0)
        md.Params.NonConvex = 2
        if GAP != None:
            md.Params.MIPGap = GAP  # 设置求解混合整数规划的Gap为GAP
        if TIMELIMITED != None:
            md.Params.TimeLimit = TIMELIMITED  # 设置最长求解时间为 TIMELIMITED 秒
        md.optimize()

        virtual_links = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            virtual_links.append(VIRTUAL_LINKS[virtual_link_index].x)

        sub_virtual_links = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            intermediate = []
            for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                intermediate.append(SUB_VIRTUAL_LINKS[virtual_link_index, sub_virtual_link_index].x)
            sub_virtual_links.append(intermediate)

        belong = []
        for message_index in range(NUMBER_OF_MESSAGES):
            intermediate_outer = []
            for virtual_link_index in range(NUMBER_OF_MESSAGES):
                intermediate_inner = []
                for sub_virtual_link_index in range(NUMBER_OF_SUB_VIRTUAL_LINKS):
                    intermediate_inner.append(int(BELONG[message_index, virtual_link_index, sub_virtual_link_index].x))
                intermediate_outer.append(intermediate_inner)
            belong.append(intermediate_outer)

        bag_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bag_of_vl.append(VALUE_OF_BAG[virtual_link_index].x)

        frame_size_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            frame_size_of_vl.append(FRAME_SIZE_OF_VL[virtual_link_index].x)

        bandwidth_of_vl = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            bandwidth_of_vl.append(BANDWIDTH_OF_VL[virtual_link_index].x)

        VL_INFORMATION = []
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            if virtual_links[ virtual_link_index ] == 1:
                vl_information = [ bag_of_vl[ virtual_link_index ], frame_size_of_vl[ virtual_link_index ], bandwidth_of_vl[ virtual_link_index ] ]
                messages_guid, logical_destination, physical_destination = [], [], []
                for sub_virtual_link_index in range( NUMBER_OF_SUB_VIRTUAL_LINKS ):
                    messages_guid_of_sub_virtual_link, logical_destination_of_sub_virtual_link, physical_destination_of_sub_virtual_link = [], [], []
                    for message_index in range( NUMBER_OF_MESSAGES ):
                        if belong[ message_index ][ virtual_link_index ][ sub_virtual_link_index ] == 1:
                            messages_guid_of_sub_virtual_link.append(self.GUID_OF_MESSAGE[message_index])
                            logical_destination_of_sub_virtual_link += self.LOGICAL_DESTINATION_OF_MESSAGE[message_index]
                            physical_destination_of_sub_virtual_link += self.PHYSICAL_DESTINATION_OF_MESSAGE[message_index]
                    messages_guid.append( messages_guid_of_sub_virtual_link )
                    logical_destination.append( logical_destination_of_sub_virtual_link )
                    physical_destination.append( physical_destination_of_sub_virtual_link )
                vl_information.append( messages_guid )
                vl_information.append( logical_destination )
                vl_information.append( physical_destination )
                VL_INFORMATION.append( vl_information )
        return VL_INFORMATION