import serial
import requests
import time



                    
# 9195791D
# 91DF811D
# 91FD351D
# 91C4A11D
# A19D291D
# 13274C91

com_port = 'COM10'

ser = serial.Serial(com_port, baudrate = 9600, timeout = 1)  # Replace 'COMX' with your port, e.g., '/dev/ttyUSB0' on Linux or 'COM3' on Windows
if not ser.isOpen():
    ser.open()
print(com_port , ' is open', ser.isOpen())

##def trigger_flask_function(action):
##    flask_url = "http://127.0.0.1:5000/trigger_function/" + action
##    response = requests.get(flask_url)
##    ser.write(response.text)
##    print(response.text)

##def trigger_flask_function(action):
##    flask_url = "http://127.0.0.1:5000/trigger_function/" + action
##    try:
##        response = requests.get(flask_url)
##        response_text = response.text.encode('utf-8')  # Convert response text to bytes
##        ser.write(response_text)  # Send response back to Arduino as bytes
##        print("Sent response to Arduino:", response.text)
##    except requests.RequestException as e:
##        print("Request failed:", e)


def trigger_flask_function(action):
    flask_url = "http://127.0.0.1:5000/trigger_function/" + action
    try:
        response = requests.get(flask_url)
        response_text = (response.text + '\n').encode('utf-8')  # Include EOL character
        ser.write(response_text)  # Send response back to Arduino as bytes with EOL
        print("Sent response to Arduino:", response.text)
        if(response.text=="no bookings"):
            pass
        else:
            ser.write(b'\n')
            ser.write(b'close\n\r')
            time.sleep(4)
            ser.write(b'open\n\r')
        time.sleep(0.2)
        

    except requests.RequestException as e:
        print("Request failed:", e)


while True:

    if ser.in_waiting > 0:
        incoming_data = ser.readline().decode().strip()
        print(f"Received data from Arduino: {incoming_data}")
##        if incoming_data == '9195791D':
##            trigger_flask_function('1') 
        try:
            if incoming_data == '9195791D':
                trigger_flask_function('1')  
            elif incoming_data == '91DF811D':
                trigger_flask_function('2')
            elif incoming_data == '91FD351D':
                trigger_flask_function('3')
            elif incoming_data == '91C4A11D':
                trigger_flask_function('4')
            elif incoming_data == 'A19D291D':
                trigger_flask_function('5')
            elif incoming_data == '13274C91':
                trigger_flask_function('6')
            elif incoming_data == '0':
                trigger_flask_function('0')
        except:
            print("network error")
