import time
import numpy as np
from dynamixel_sdk import *

ADDR_MX_TORQUE_ENABLE         = 24
ADDR_MX_CW_COMPLIANCE_MARGIN  = 26
ADDR_MX_CCW_COMPLIANCE_MARGIN = 27
ADDR_MX_CW_COMPLIANCE_SLOPE   = 28
ADDR_MX_CCW_COMPLIANCE_SLOPE  = 29
ADDR_MX_GOAL_POSITION         = 30
ADDR_MX_MOVING_SPEED          = 32
ADDR_MX_PRESENT_POSITION      = 36
ADDR_MX_PUNCH                 = 48
PROTOCOL_VERSION              = 1.0
DXL_IDS                       = [1,2,3,4]
DEVICENAME                    = '/dev/ttyACM0'
BAUDRATE                      = 1000000
TORQUE_ENABLE                 = 1
TORQUE_DISABLE                = 0
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)
portHandler.openPort()
portHandler.setBaudRate(BAUDRATE)
for DXL_ID in DXL_IDS:
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_CW_COMPLIANCE_MARGIN, 5)
    packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_CCW_COMPLIANCE_MARGIN, 5)
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_CW_COMPLIANCE_SLOPE, 128)
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_CCW_COMPLIANCE_SLOPE, 128)
    packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_MOVING_SPEED, 1023)

# Motor range found from live test
MOTOR_RANGE = {
    1: [0, 1023],
    2: [200, 900],
    3: [50, 950],
    4: [150, 850],
}
MOTOR_CENTER = 512
MOTOR_VALUE_RAD = 5.2360 / 1023.0

def set_motor_pos(motor_id, radians):
    if motor_id == 2:
        radians -= np.pi / 2

    value = int(MOTOR_CENTER + radians / MOTOR_VALUE_RAD)

    # Check if value is within motor range
    if value < MOTOR_RANGE[motor_id][0]:
        value = MOTOR_RANGE[motor_id][0]
        print("Value too low")
    elif value > MOTOR_RANGE[motor_id][1]:
        print("Value too high")
        value = MOTOR_RANGE[motor_id][1]

    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, motor_id, ADDR_MX_GOAL_POSITION, value)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def Config4DOF(o4, x4_z, d1, a2, a3, a4):
    q1 = np.arctan2(o4[1], o4[0])

    x4_0 = np.array([
        np.sqrt(1 - x4_z**2) * np.cos(q1),
        np.sqrt(1 - x4_z**2) * np.sin(q1),
        x4_z
    ])

    oc = o4 - a4 * x4_0

    s = oc[2] - d1
    r = np.sqrt(oc[0]**2 + oc[1]**2)
    c3 = (r**2 + s**2 - a2**2 - a3**2) / (2 * a2 * a3)

    q3 = np.arctan2(np.sqrt(1 - c3**2), c3)
    q2 = np.arctan2(s, r) - np.arctan2(a3 * np.sin(q3), a2 + a3 * c3)
    q4 = np.arcsin(x4_z) - (q2 + q3)

    return q1, q2, q3, q4


q1, q2, q3, q4 = Config4DOF(np.array([0,-0.15,0.12]), 0, 0.05, 0.093, 0.093, 0.05)

# Print q1, q2, q3, q4 in degrees
print(np.degrees([q1, q2, q3, q4]))

set_motor_pos(1, q1)
set_motor_pos(2, q2)
set_motor_pos(3, q3)
set_motor_pos(4, q4)

time.sleep(1)
# Disable Dynamixel Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))

# Close port
portHandler.closePort()