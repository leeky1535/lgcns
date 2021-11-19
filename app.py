# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import threading
import time
import json

#Flask 객체 인스턴스 생성
app = Flask(__name__)
app.secret_key ='lgcns'
socketio = SocketIO(app)
agv_info_list = []
agv_count = 0
alarmCD = {11 : '현 위치확인 안됨',
          12 : '직진 후, 위치 오류',
          13 : '우 90도회전 후, 위치 오류',
          14 : '좌 90도회전 후, 위치 오류',
          15 : '180도 회전 후, 위치 오류',
          16 : '후진 후, 위치 오류',
          21 : 'LOW BATTERY',
          22 : '과전류 발생',
          31 : 'Belt 구동 실패',
          32 : 'Tray 구동 실패'}


@app.route('/') # 서버에서 보는 화면
def index():
  global agv_info_list
  global agv_count
  agv_count = 0
  agv_info_list = []
  return render_template('index.html')

@app.route('/agv', methods=['GET', 'POST']) # AGV 연결 페이지
def agv():
  agvNo = request.args.get("agvNo")
  print(agvNo)
  return render_template('agv.html', no=agvNo)

@app.route('/clients', methods=['GET', 'POST']) # AGV 연결 페이지
def clients_view_page():
  return render_template('clients.html')

@socketio.on('connect')
def connect():
  print("connected")

@socketio.on('disconnect')
def disconnect():
  print("disconnect")

@socketio.on('authenticate')
def authenticate(data):
  global agv_info_list
  agvNo = data['AGV_NO']
  location = data['LOCATION']
  for agv in agv_info_list:
    if agv['AGV_NO'] == agvNo or agv['LOCATION'] == location:
      socketio.emit('authenticationFail', data)
      return
  agv_info_list.append(data)
  socketio.emit('authenticationSuccess', data)


@socketio.on('agvStatusResponse')
def collectAgvStatus(agvStatus, methods=['GET', 'POST']):
  global agv_info_list
  agv_info_list.append(agvStatus)
  print(agvStatus)
  socketio.emit('agvStatusToIndex', agvStatus)


@socketio.on('agvStatusRequestFromIndex')
def requestAgvStatus(agvNo):
  socketio.emit('agvStatusRequest', agvNo)
  global agv_info_list
  agv_info_list = []

@socketio.on('alarmFromClient')
def alarm(data):
  socketio.emit('alarmToIndex', data)

@socketio.on('alarmStopFromClient')
def alarmStop(agvNo):
  socketio.emit('alarmStopToIndex', agvNo)



if __name__=="__main__":
  socketio.run(app, debug=True)
  # host 등을 직접 지정하고 싶다면
  # app.run(host="127.0.0.1", port="5000", debug=True)