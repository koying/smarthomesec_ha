# -*- coding: utf-8 -*-

#################################################################################################

import json
import logging
import re
import threading
import ssl
import certifi

import websocket

from custom_components.smarthomesec.const import API_BASEHOST

##################################################################################################

LOG = logging.getLogger(__name__)

##################################################################################################


class WSClient(threading.Thread):
    global_wsc = None
    global_stop = False

    def __init__(self, client, token):
        LOG.debug("WSClient initializing...")

        self.client = client
        self.token = token

        self.keepalive = None
        self.wsc = None
        self.stop = False

        threading.Thread.__init__(self)

    def send(self, code, data=""):
        if self.wsc is None:
            raise ValueError("The websocket client is not started.")

        self.wsc.send(code + data)

    def run(self):
        wsc_url = (
            f"wss://{API_BASEHOST}/ws/socket.io/?token=%s&transport=websocket"
            % (self.token)
        )

        LOG.debug("Websocket url: %s", wsc_url)

        self.wsc = websocket.WebSocketApp(
            wsc_url,
            on_message=lambda ws, message: self.on_message(ws, message),
            on_error=lambda ws, error: self.on_error(ws, error),
            on_ping=lambda ws, message: self.on_ping(ws, message),
            on_pong=lambda ws, message: self.on_pong(ws, message),
        )
        self.wsc.on_open = lambda ws: self.on_open(ws)

        if self.global_wsc is not None:
            self.global_wsc.close()
        self.global_wsc = self.wsc

        while not self.stop and not self.global_stop:
            self.wsc.run_forever(ping_interval=10, sslopt={"ca_certs": certifi.where()})

            if not self.stop:
                break

        LOG.debug("---<[ websocket ]")
        self.client.callback("WebSocketDisconnect", None)

    def on_error(self, ws, error):
        LOG.error(error)
        self.client.callback("WebSocketError", error)

    def on_open(self, ws):
        LOG.debug("--->[ websocket ]")
        self.client.callback("WebSocketConnect", None)

    def on_ping(self, ws, message):
        LOG.debug("--->[ websocket ] Got a ping! A pong reply has already been automatically sent.")

    def on_pong(self, ws, message):
        LOG.debug("--->[ websocket ] Got a pong! Sending keepalive")
        self.send("2")

    def on_message(self, ws, message):
        re_split = re.search("^(\\d+)(.*)$", message)
        code = re_split.group(1)
        content = re_split.group(2)

        LOG.debug("Received: code: %s; message: %s", code, content)
        self.client.callback(code, content)

        return

        message = json.loads(message)

        data = message.get("Data", {})

        if message["MessageType"] == "ForceKeepAlive":
            self.send("KeepAlive")
            if self.keepalive is not None:
                self.keepalive.stop()
            self.keepalive = KeepAlive(data, self)
            self.keepalive.start()
            LOG.debug("ForceKeepAlive received from server.")
            return
        elif message["MessageType"] == "KeepAlive":
            LOG.debug("KeepAlive received from server.")
            return

        if data is None:
            data = {}
        elif not isinstance(data, dict):
            data = {"value": data}

        if not self.client.config.data["app.default"]:
            data["ServerId"] = self.client.auth.server_id

        self.client.callback(message["MessageType"], data)

    def stop_client(self):
        self.stop = True

        if self.keepalive is not None:
            self.keepalive.stop()

        if self.wsc is not None:
            self.wsc.close()

        self.global_stop = True
        self.global_wsc = None
