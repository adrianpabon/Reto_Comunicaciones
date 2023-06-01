# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 15:43:51 2022

@author: angelosoto & alvarobaez
"""
#%%
import websocket
import json
import pandas as pd
import math
import time
import streamlit as st
#access_token = 'vn4GngAAAA11czEubG9yaW90Lmlve8AGYpWyWCFvz1vohYuCmQ=='
access_token = 'vn4GngAAAA11czEubG9yaW90LmlvRWs7K0zWDjztsa5_i3iWLg=='
totalPages = 1
page = 1
dataTemporal = []
dataTotal = []
gateways = []
devices = []
llavecitas=['nc','v1','v2','v3','v4','v5','v6','v7','v8','v9','v10','v11']
def extract_elements_by_index(lst, index):
    selected_elements = [sublist[index] for sublist in lst]
    return selected_elements
def list_to_dict(lst_keys, lst_values):
    my_dict = {key: value for key, value in zip(lst_keys, lst_values)}
    return my_dict
def replace_value_in_list(lst, old_value, new_value):
    for i in range(len(lst)):
        if lst[i] == old_value:
            lst[i] = new_value
    return lst
def separar_cadena8(cadena):
    separaciones = []
    for i in range(0, len(cadena), 8):
        separacion = cadena[i:i+8]
        separaciones.append(separacion)
    return separaciones
def separar_cadena2(cadena):
    separaciones = []
    for i in range(0, len(cadena), 2):
        separacion = cadena[i:i+2]
        separaciones.append(separacion)
    return separaciones
def decode_hex_to_float(hex_numbers):
    hex_values = [int(hex_num, 16) for hex_num in hex_numbers]
    hex_string = ''.join([format(hex_val, '08b') for hex_val in hex_values])
    sign = -1 if hex_string[0] == '1' else 1
    exponent = int(hex_string[1:9], 2) - 127
    mantissa = 1 + sum(int(bit) / (2 ** (i + 1)) for i, bit in enumerate(hex_string[9:]))
    return sign * mantissa * (2 ** exponent)
def saveData(data_json):
     data1 = pd.json_normalize(data_json)
     data2 = pd.json_normalize(data_json,record_path=['gws'])
     data_frame = pd.concat([data1,data2],axis=1)
     del data_frame['gws']
     data_frame.to_excel(r"/home/pablo/signals/Loriot.xlsx")
     return

def convertir_string(cadena):
    longitud = len(cadena)
    cuarto = longitud // 4
    cuart = cadena[3*cuarto:]
    mitad = cadena[2*cuarto:3*cuarto]
    trescua = cadena[cuarto:2*cuarto]
    final = cadena[:cuarto]
    nueva_cadena = cuart + mitad+trescua+final
    return nueva_cadena

def consumeWS(page=1):
    global totalPages, dataTemporal, dataTotal
    perPage = 100

    dataRequest = {
        'cmd': 'cq',
        'filter' : {
            'from' : "1684503949983",
            "EUI"  : "4768B269001B0048"
        },
        'perPage': perPage,
        'page': str(page)
    }

    def on_message(ws, message):
        global totalPages, dataTemporal, dataTotal
        message = json.loads(message)
        messagelist=message['cache']
        histoinfo=[]
        for i in range(10):
            messagedict=messagelist[1]
            denviado=messagedict['data']
            edato=separar_cadena8(denviado)
            decodato=[]
            for i in range(0,len(edato)):
                edato3=separar_cadena2(convertir_string(edato[i]))
                helpp=decode_hex_to_float(edato3)
                if helpp==5.104235503814077e+38:
                    helpp="NAN"
                print(helpp)
                decodato.append(helpp)
            histoinfo.append(decodato)
        print(histoinfo)
        clhisto=[]
        for i in range(0, len(histoinfo[0])):
            clhisto.append(extract_elements_by_index(histoinfo,i))
        option = st.selectbox(
                'Select please',
                            ('Last message', 'Last 10 messages'))

        if option=='Last message':
            dictdis= list_to_dict(llavecitas,histoinfo[0])
            st.table(dictdis)
        if option=='Last 10 messages':
            dictdis = list_to_dict(llavecitas, clhisto)
            st.table(dictdis)
        if message['cmd'] == "cq":
            if page == 1:
                dataTemporal = message['cache']
            else:
                dataTemporal += message['cache']
            
        return;
        ws.close()
        if page < totalPages:
            nextPage = page + 1
            consumeWS(nextPage)
        elif page == totalPages:
            dataTotal = dataTemporal
            # saveData(dataTotal)
            return;




    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("Connection closed")


    def on_open(ws):
        ws.send(json.dumps(dataRequest))
        print("Connection established")

    
    websocket.enableTrace(False)
    ws_url = f"wss://us1.loriot.io/app?token={access_token}"
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
      #  on_close=on_close,
        on_open=on_open,
    )

    ws.run_forever()


consumeWS()

