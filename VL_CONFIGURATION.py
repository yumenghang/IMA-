# _*_ coding:utf-8 _*_
"""


"""
import numpy as np
from gurobipy import *
import OPTIMIZATION_MODEL
import MESSAGES_PROCESSING

if __name__ == "__main__":
    messages_per_physical_port = np.load( "INTERMEDIATE_FILE/messages_per_physical_port.npy", allow_pickle='TRUE').item()
    physical_ports_information = np.load( "INTERMEDIATE_FILE/physical_ports_information.npy", allow_pickle='TRUE').item()
    VL_DICT_OF_A_NET, VL_DICT_OF_B_NET = dict(), dict()
    GAP, TIMELIMITED = None, None
    for key in list( messages_per_physical_port.keys() ):
        messages_of_physical_port = messages_per_physical_port[ key ]
        messages_preprocessed = MESSAGES_PROCESSING.MESSAGES_PREPROCESSED()
        RETURNED_VL_DICT_LIST = messages_preprocessed.messages_preprocessed( messages_of_physical_port, physical_ports_information, VL_DICT_OF_A_NET, VL_DICT_OF_B_NET, GAP, TIMELIMITED  )
        if RETURNED_VL_DICT_LIST != []:
            VL_DICT_OF_A_NET, VL_DICT_OF_B_NET = RETURNED_VL_DICT_LIST[0], RETURNED_VL_DICT_LIST[1]
        else:
            continue
    #保存文件
    np.save('VL_DICT_OF_A_NET.npy', VL_DICT_OF_A_NET)
    np.save('VL_DICT_OF_B_NET.npy', VL_DICT_OF_B_NET)
    #读取方式
    #messages_info = np.load( 'messages_info.npy', allow_pickle='TRUE').item()