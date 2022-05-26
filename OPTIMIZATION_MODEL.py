import numpy as np
from gurobipy import *

HEAD_OF_FRAME = 47  # 虚链路帧头大小
MINIMUM_FRAME = 17  # 最小帧长（不包括帧头）
MAXIMUM_FRAME = 1471  # 最大帧长（不包括帧头）
LATENCY_LIMITED_FRACTION = 1/2 # 表示以系统对消息时延要求的LATENCY_LIMITED_FRACTION作为消息除路由外的时间限制
MAX = sys.maxsize

class VL_OF_RDIU():
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

    def vl_of_rdiu_with_period(self, GAP, TIMELIMITED):
        NUMBER_OF_MESSAGES = len(self.SIZE_OF_MESSAGE)  # 消息的数目

        md = Model("Integer Linear Programming")

        VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="VIRTUAL_LINKS")  # 一维数组：长度为NUMBER_OF_MESSAGES，记录虚链路的分布。取值为0或1，当取值为1时，表示有此条虚拟链路；取值为0时，表示无此条虚拟链路
        BELONG = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="BELONG")  # 消息j与虚拟链路VL的对应关系，前一个NUMBER_OF_MESSAGES表示消息，后一个NUMBER_OF_MESSAGES表示虚链路，综合表示一条消息是否属于虚链路

        # 一维数组，记录：每一条虚链路VL的切片数目。注意，这里虚链路的切片数目满足：(NUM-1)*MTU <SIZE <= NUM*MTU，即：确定了NUMBER_OF_FRAMES_OF_VL的上、下确界（注：SIZE表示所有属于此虚链路的消息的大小之和）
        NUMBER_OF_FRAMES_OF_VL = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_VL")
        # 一维数组，记录：每条消息的切片数目。注意，这里消息的切片数目满足：(num-1)*MTU < size <= num*MTU，即：确定了number_of_frames_of_message的上、下确界（注：size表示所有属于此消息的大小）
        NUMBER_OF_FRAMES_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_MESSAGES")
        FRAME_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_VL")  # 记录每一条虚链路VL的MTU大小
        FRAME_SIZE_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_MESSAGES")  # 记录每一条消息的MTU大小，其大小等于该消息所属的虚链路的MTU大小

        UPPER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_VL")  # 一维数组，记录：每一条虚链路的：NUMBER_OF_FRAMES_OF_VL*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的上确界
        LOWER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="LOWER_BOUND_OF_TOTAL_SIZE_OF_VL")  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_VL-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的下确界
        upper_bound_of_total_size_of_messages = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="upper_bound_of_total_size_of_messages")  # 一维数组，记录：每一条消息的：NUMBER_OF_FRAMES_OF_MESSAGES*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的上确界
        lower_bound_of_total_size_of_messages = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="lower_bound_of_total_size_of_messages")  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_MESSAGES-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的下确界

        VALUE_OF_K = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=2048, vtype=GRB.INTEGER, name="VALUE_OF_K")  # 一维数组，记录：每一条虚拟链路VL的BAG的参数
        VALUE_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="VALUE_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的大小
        RECIPROCAL_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="RECIPROCAL_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的倒数
        SUM_OF_BAG_OF_ALL_VL = md.addVar(vtype=GRB.CONTINUOUS, name="SUM_OF_BAG_OF_ALL_VL")  # 一维数组，记录：所有虚链路VL的一个BAG之和
        CYCLE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="CYCLE_OF_VL")  # 一维数组，记录：每一条虚链路的真实传输时延，其大小为：（该消息所属虚链路VL的切片数目-1） * SUM_OF_BAG_OF_ALL_VL

        BANDWIDTH_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_VL")  # 一维数组，记录：每一条虚拟链路VL的带宽
        BANDWIDTH_OF_EXISTING_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_EXISTING_VL")  # 一维数组，记录：真实存在的虚拟链路VL的带宽占用，其值等于：BANDWIDTH_OF_VL*VIRTUAL_LINKS（注：这里的真实存在表示VIRTUAL_LINKS数组中对应取值为1）

        # 约束：一条消息只能同时属于一条虚拟链路
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) == 1)
        # 约束：所有消息都必须有属于的一条虚拟链路VL
        # 约束：结合上一条约束，达到约束效果：所有消息都必须属于且仅能属于一条真实存在的虚拟链路VL
        md.addConstr(quicksum(quicksum(BELONG[message_index, virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) for message_index in range(NUMBER_OF_MESSAGES)) == NUMBER_OF_MESSAGES)
        # 约束：BELONG数组中，某一列（对应某一虚拟链路VL）中元素全为0时，表示没有消息属于此虚拟链路，因此该条虚拟链路不应该存在，所以限制其值必须取为0
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VIRTUAL_LINKS[virtual_link_index] <= quicksum(BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))

        # 约束：消息的帧大小等于该消息所属的虚拟链路的帧大小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(FRAME_SIZE_OF_MESSAGES[message_index] == quicksum(FRAME_SIZE_OF_VL[virtual_link_index] * BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))

        # 约束：根据虚拟链路BAG参数的取值，确定BAG的大小和BAG的倒数
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VALUE_OF_BAG[virtual_link_index] == VALUE_OF_K[virtual_link_index] / 2)
            md.addConstr(VALUE_OF_BAG[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index] == 1)

        # 约束：所有真实存在的虚拟链路的一个BAG之和
        md.addConstr(SUM_OF_BAG_OF_ALL_VL == quicksum(VALUE_OF_BAG[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))

        # 约束：确定NUMBER_OF_FRAMES_OF_VL，既要保证足够大，能够把所有消息的内容传输完毕，也不能够太大
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == NUMBER_OF_FRAMES_OF_VL[virtual_link_index] * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] >= quicksum(self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] <= quicksum(self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            # 约束：每一条虚链路VL的传输时延（注：此虚链路VL上所有消息切片传输完毕）
            md.addConstr(CYCLE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * SUM_OF_BAG_OF_ALL_VL)
        # 约束：每一条消息的传输时延等于其所属的虚链路VL的传输时延，因此要约束其小于系统对此条消息的传输时延要求
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(CYCLE_OF_VL[virtual_link_index] * BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) <= self.DELAY_BOUND_OF_MESSAGE[message_index] * LATENCY_LIMITED_FRACTION)

        # 约束：每一条消息的切片数目既不可太大，也不可太小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr( upper_bound_of_total_size_of_messages[ message_index ] == NUMBER_OF_FRAMES_OF_MESSAGES[ message_index ] * FRAME_SIZE_OF_MESSAGES[ message_index ] )
            md.addConstr( upper_bound_of_total_size_of_messages[ message_index ] >= self.SIZE_OF_MESSAGE[ message_index ] )
        # 约束：频率约束
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(NUMBER_OF_FRAMES_OF_MESSAGES[message_index] * BELONG[message_index, virtual_link_index] / self.PERIOD_OF_MESSAGE[message_index] for message_index in range(NUMBER_OF_MESSAGES)) <= RECIPROCAL_OF_BAG[virtual_link_index])

        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BANDWIDTH_OF_VL[virtual_link_index] == HEAD_OF_FRAME * RECIPROCAL_OF_BAG[virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index])
            md.addConstr(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] == BANDWIDTH_OF_VL[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index])

        md.setObjective(quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)), GRB.MINIMIZE)
        md.Params.NonConvex = 2
        md.setParam('OutputFlag', 0)
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
                messages_guid, logical_destination, physical_destination = [], [], []
                for message_index in range( len( belong ) ):
                    if belong[ message_index ][ virtual_link_index ] == 1:
                        messages_guid.append( self.GUID_OF_MESSAGE[ message_index ] )
                        logical_destination += self.LOGICAL_DESTINATION_OF_MESSAGE[ message_index ]
                        physical_destination +=  self.PHYSICAL_DESTINATION_OF_MESSAGE[ message_index ]
                vl_information.append( messages_guid )
                vl_information.append( logical_destination )
                vl_information.append( physical_destination )
                VL_INFORMATION.append( vl_information )
        return VL_INFORMATION

    def vl_of_rdiu_no_period(self, GAP, TIMELIMITED):
        NUMBER_OF_MESSAGES = len(self.SIZE_OF_MESSAGE)  # 消息的数目

        md = Model("Integer Linear Programming")

        VIRTUAL_LINKS = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="VIRTUAL_LINKS")  # 一维数组：长度为NUMBER_OF_MESSAGES，记录虚链路的分布。取值为0或1，当取值为1时，表示有此条虚拟链路；取值为0时，表示无此条虚拟链路
        BELONG = md.addVars(NUMBER_OF_MESSAGES, NUMBER_OF_MESSAGES, vtype=GRB.BINARY, name="BELONG")  # 消息j与虚拟链路VL的对应关系，前一个NUMBER_OF_MESSAGES表示消息，后一个NUMBER_OF_MESSAGES表示虚链路，综合表示一条消息是否属于虚链路

        # 一维数组，记录：每一条虚链路VL的切片数目。注意，这里虚链路的切片数目满足：(NUM-1)*MTU <SIZE <= NUM*MTU，即：确定了NUMBER_OF_FRAMES_OF_VL的上、下确界（注：SIZE表示所有属于此虚链路的消息的大小之和）
        NUMBER_OF_FRAMES_OF_VL = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_VL")
        # 一维数组，记录：每条消息的切片数目。注意，这里消息的切片数目满足：(num-1)*MTU < size <= num*MTU，即：确定了number_of_frames_of_message的上、下确界（注：size表示所有属于此消息的大小）
        NUMBER_OF_FRAMES_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=MAX, vtype=GRB.INTEGER, name="NUMBER_OF_FRAMES_OF_MESSAGES")
        FRAME_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_VL")  # 记录每一条虚链路VL的MTU大小
        FRAME_SIZE_OF_MESSAGES = md.addVars(NUMBER_OF_MESSAGES, lb=MINIMUM_FRAME, ub=MAXIMUM_FRAME, vtype=GRB.INTEGER, name="FRAME_SIZE_OF_MESSAGES")  # 记录每一条消息的MTU大小，其大小等于该消息所属的虚链路的MTU大小

        UPPER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="UPPER_BOUND_OF_TOTAL_SIZE_OF_VL")  # 一维数组，记录：每一条虚链路的：NUMBER_OF_FRAMES_OF_VL*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的上确界
        LOWER_BOUND_OF_TOTAL_SIZE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="LOWER_BOUND_OF_TOTAL_SIZE_OF_VL")  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_VL-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_VL的下确界
        upper_bound_of_total_size_of_messages = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="upper_bound_of_total_size_of_messages")  # 一维数组，记录：每一条消息的：NUMBER_OF_FRAMES_OF_MESSAGES*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的上确界
        lower_bound_of_total_size_of_messages = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.INTEGER, name="lower_bound_of_total_size_of_messages")  # 一维数组，记录：每一条虚链路的：(NUMBER_OF_FRAMES_OF_MESSAGES-1)*FRAME_SIZE_OF_VL，即用来确定NUMBER_OF_FRAMES_OF_MESSAGES的下确界

        VALUE_OF_K = md.addVars(NUMBER_OF_MESSAGES, lb=1, ub=2048, vtype=GRB.INTEGER, name="VALUE_OF_K")  # 一维数组，记录：每一条虚拟链路VL的BAG的参数
        VALUE_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, lb=0.5, ub=1024, vtype=GRB.CONTINUOUS, name="VALUE_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的大小
        RECIPROCAL_OF_BAG = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="RECIPROCAL_OF_BAG")  # 一维数组，记录：每一条虚拟链路VL的BAG的倒数
        SUM_OF_BAG_OF_ALL_VL = md.addVar(vtype=GRB.CONTINUOUS, name="SUM_OF_BAG_OF_ALL_VL")  # 一维数组，记录：所有虚链路VL的一个BAG之和
        CYCLE_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="CYCLE_OF_VL")  # 一维数组，记录：每一条虚链路的真实传输时延，其大小为：（该消息所属虚链路VL的切片数目-1） * SUM_OF_BAG_OF_ALL_VL

        BANDWIDTH_OF_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_VL")  # 一维数组，记录：每一条虚拟链路VL的带宽
        BANDWIDTH_OF_EXISTING_VL = md.addVars(NUMBER_OF_MESSAGES, vtype=GRB.CONTINUOUS, name="BANDWIDTH_OF_EXISTING_VL")  # 一维数组，记录：真实存在的虚拟链路VL的带宽占用，其值等于：BANDWIDTH_OF_VL*VIRTUAL_LINKS（注：这里的真实存在表示VIRTUAL_LINKS数组中对应取值为1）

        # 约束：一条消息只能同时属于一条虚拟链路
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) == 1)
        # 约束：所有消息都必须有属于的一条虚拟链路VL
        # 约束：结合上一条约束，达到约束效果：所有消息都必须属于且仅能属于一条真实存在的虚拟链路VL
        md.addConstr(quicksum(quicksum(BELONG[message_index, virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) for message_index in range(NUMBER_OF_MESSAGES)) == NUMBER_OF_MESSAGES)
        # 约束：BELONG数组中，某一列（对应某一虚拟链路VL）中元素全为0时，表示没有消息属于此虚拟链路，因此该条虚拟链路不应该存在，所以限制其值必须取为0
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VIRTUAL_LINKS[virtual_link_index] <= quicksum(BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))

        # 约束：消息的帧大小等于该消息所属的虚拟链路的帧大小
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(FRAME_SIZE_OF_MESSAGES[message_index] == quicksum(FRAME_SIZE_OF_VL[virtual_link_index] * BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))

        # 约束：根据虚拟链路BAG参数的取值，确定BAG的大小和BAG的倒数
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(VALUE_OF_BAG[virtual_link_index] == VALUE_OF_K[virtual_link_index] / 2)
            md.addConstr(VALUE_OF_BAG[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index] == 1)

        # 约束：所有真实存在的虚拟链路的一个BAG之和
        md.addConstr(SUM_OF_BAG_OF_ALL_VL == quicksum(VALUE_OF_BAG[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)))

        # 约束：确定NUMBER_OF_FRAMES_OF_VL，既要保证足够大，能够把所有消息的内容传输完毕，也不能够太大
        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == NUMBER_OF_FRAMES_OF_VL[virtual_link_index] * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * FRAME_SIZE_OF_VL[virtual_link_index])
            md.addConstr(UPPER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] >= quicksum(self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            md.addConstr(LOWER_BOUND_OF_TOTAL_SIZE_OF_VL[virtual_link_index] <= quicksum(self.SIZE_OF_MESSAGE[message_index] * BELONG[message_index, virtual_link_index] for message_index in range(NUMBER_OF_MESSAGES)))
            # 约束：每一条虚链路VL的传输时延（注：此虚链路VL上所有消息切片传输完毕）
            md.addConstr(CYCLE_OF_VL[virtual_link_index] == (NUMBER_OF_FRAMES_OF_VL[virtual_link_index] - 1) * SUM_OF_BAG_OF_ALL_VL)
        # 约束：每一条消息的传输时延等于其所属的虚链路VL的传输时延，因此要约束其小于系统对此条消息的传输时延要求
        for message_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(quicksum(CYCLE_OF_VL[virtual_link_index] * BELONG[message_index, virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)) <= self.DELAY_BOUND_OF_MESSAGE[message_index] * LATENCY_LIMITED_FRACTION)

        for virtual_link_index in range(NUMBER_OF_MESSAGES):
            md.addConstr(BANDWIDTH_OF_VL[virtual_link_index] == HEAD_OF_FRAME * RECIPROCAL_OF_BAG[virtual_link_index] + FRAME_SIZE_OF_VL[virtual_link_index] * RECIPROCAL_OF_BAG[virtual_link_index])
            md.addConstr(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] == BANDWIDTH_OF_VL[virtual_link_index] * VIRTUAL_LINKS[virtual_link_index])

        md.setObjective(quicksum(BANDWIDTH_OF_EXISTING_VL[virtual_link_index] for virtual_link_index in range(NUMBER_OF_MESSAGES)), GRB.MINIMIZE)
        md.Params.NonConvex = 2
        md.setParam('OutputFlag', 0)
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
                messages_guid, logical_destination, physical_destination = [], [], []
                for message_index in range( len( belong ) ):
                    if belong[ message_index ][ virtual_link_index ] == 1:
                        messages_guid.append( self.GUID_OF_MESSAGE[ message_index ] )
                        logical_destination += self.LOGICAL_DESTINATION_OF_MESSAGE[ message_index ]
                        physical_destination += self.PHYSICAL_DESTINATION_OF_MESSAGE[ message_index ]
                vl_information.append( messages_guid )
                vl_information.append( logical_destination )
                vl_information.append( physical_destination )
                VL_INFORMATION.append( vl_information )
        return VL_INFORMATION