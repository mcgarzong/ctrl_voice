import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, result):
    print("El comando ha sido enviado correctamente 🎤")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("VOZ-ESCENA-C")
client1.on_message = on_message

st.title("🎭 VOZ EN ESCENA")
st.subheader("Control por voz de tu teatro inteligente")

image = Image.open('teatro.jpeg')
st.image(image, width=250)

st.write("🎙️ **Toca el botón, da tu comando y deja que el teatro cobre vida.**")
st.markdown("---")

st.markdown("### 🎬 Comandos disponibles:")
st.write("💡 **“Encender las luces del escenario”**")
st.write("🌙 **“Apagar las luces del escenario”**")
st.write("🎵 **“Prender la música de la escena”**")
st.write("🔇 **“Silenciar el teatro”**")
st.markdown("---")

stt_button = Button(label="🎤 Comenzar actuación", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.lang = "es-ES";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        user_command = result.get("GET_TEXT").strip()
        st.success(f"🎧 Comando detectado: “{user_command}”")
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": user_command})
        ret = client1.publish("voz_en_escena", message)
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass
