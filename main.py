import random
import string
import json
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

Window.softinput_mode = 'resize'
FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # We save this as self.main_layout so our keyboard function can find it
        self.main_layout = BoxLayout(
            orientation='vertical', 
            padding=40, 
            spacing=25, 
            size_hint=(0.9, 0.7), 
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        title = Label(
            text="ORANGE CHAT", 
            font_size="32sp", 
            bold=True,
            color=[1, 0.43, 0, 1],
            size_hint_y=None,
            height="50dp"
        )
        self.main_layout.add_widget(title)
        
        self.username_input = TextInput(
            hint_text="Enter your Username",
            multiline=False,
            padding=[15, 15, 15, 15],
            background_color=[0.2, 0.2, 0.2, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.6, 0.6, 0.6, 1],
            size_hint_y=None,
            height="50dp"
        )
        self.main_layout.add_widget(self.username_input)
        
        self.room_input = TextInput(
            hint_text="Enter Room ID (To Join)",
            multiline=False,
            padding=[15, 15, 15, 15],
            background_color=[0.2, 0.2, 0.2, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.6, 0.6, 0.6, 1],
            size_hint_y=None,
            height="50dp"
        )
        self.main_layout.add_widget(self.room_input)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height="50dp")
        
        join_btn = Button(
            text="Join Room",
            background_normal='',
            background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1],
            bold=True,
            on_release=self.join_room
        )
        
        create_btn = Button(
            text="Create New Room",
            background_normal='',
            background_color=[0.2, 0.2, 0.2, 1],
            color=[1, 0.43, 0, 1],
            bold=True,
            on_release=self.create_room
        )
        
        btn_layout.add_widget(join_btn)
        btn_layout.add_widget(create_btn)
        self.main_layout.add_widget(btn_layout)
        
        self.status_label = Label(text="", color=[1, 0, 0, 1], size_hint_y=None, height="30dp")
        self.main_layout.add_widget(self.status_label)
        
        self.add_widget(self.main_layout)
        
        # Listen for keyboard on the home screen layout
        Window.bind(on_keyboard_height=self.adjust_for_keyboard)

    def adjust_for_keyboard(self, window, height):
        if height > 0:
            # Shift up the login panel layout manually
            self.main_layout.pos_hint = {"center_x": 0.5, "center_y": 0.75}
        else:
            self.main_layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def get_user_details(self):
        username = self.username_input.text.strip()
        if not username:
            self.status_label.text = "Username cannot be empty!"
            return None
        return username

    def join_room(self, instance):
        username = self.get_user_details()
        room_id = self.room_input.text.strip().upper()
        if username and room_id:
            self.status_label.text = "Connecting..."
            UrlRequest(
                f"{FIREBASE_URL}rooms/{room_id}.json",
                on_success=lambda req, res: self.on_join_success(res, username, room_id),
                on_failure=self.on_net_error,
                on_error=self.on_net_error,
                timeout=4 
            )

    def on_join_success(self, result, username, room_id):
        if result is not None:
            self.switch_to_chat(username, room_id)
        else:
            self.status_label.text = "Room ID does not exist!"

    def create_room(self, instance):
        username = self.get_user_details()
        if username:
            self.status_label.text = "Creating Room..."
            room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            initial_data = json.dumps({"created_by": username, "messages": ""})
            UrlRequest(
                f"{FIREBASE_URL}rooms/{room_id}.json",
                req_body=initial_data,
                method='PUT',
                on_success=lambda req, res: self.switch_to_chat(username, room_id),
                on_failure=self.on_net_error,
                on_error=self.on_net_error,
                timeout=4
            )

    def on_net_error(self, req, error):
        self.status_label.text = "Connection timed out! Try again."

    def switch_to_chat(self, username, room_id):
        self.status_label.text = ""
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_room(username, room_id)
        self.manager.current = 'chat'


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.room_id = ""
        self.last_fetched_keys = set()
        
        with self.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = BoxLayout(orientation='vertical')
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height="56dp", padding=10)
        with header.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(
            text="< Leave", 
            size_hint_x=None, 
            width="90dp",
            background_normal='',
            background_color=[0.07, 0.07, 0.07, 1],
            color=[1, 0.43, 0, 1],
            on_release=lambda x: self.leave_room()
        )
        header.add_widget(back_btn)
        
        self.title_label = Label(text="Room: ----", color=[1, 0.43, 0, 1], font_size="18sp", bold=True)
        header.add_widget(self.title_label)
        self.layout.add_widget(header)
        
        scroll = ScrollView()
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        scroll.add_widget(self.chat_list)
        self.layout.add_widget(scroll)
        
        input_layout = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height="60dp", spacing=10)
        self.msg_input = TextInput(
            hint_text="Type a message...",
            multiline=False,
            background_color=[0.2, 0.2, 0.2, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.6, 0.6, 0.6, 1]
        )
        send_btn = Button(
            text="SEND", 
            size_hint_x=None, 
            width="80dp",
            background_normal='',
            background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1],
            bold=True,
            on_release=self.send_message
        )
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(send_btn)
        self.layout.add_widget(input_layout)
        
        self.add_widget(self.layout)
        
        # Listen for keyboard inside the chat room screen
        Window.bind(on_keyboard_height=self.adjust_chat_layout)

    def adjust_chat_layout(self, window, height):
        if height > 0:
            # Manually pull up the layout bottom padding to clear keyboard space
            self.layout.padding = [0, 0, 0, height]
        else:
            self.layout.padding = [0, 0, 0, 0]

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def setup_room(self, username, room_id):
        self.username = username
        self.room_id = room_id
        self.title_label.text = f"Room: {room_id}"
        self.chat_list.clear_widgets()
        self.last_fetched_keys.clear()
        Clock.schedule_interval(self.fetch_messages, 0.5)

    def send_message(self, instance):
        msg_text = self.msg_input.text.strip()
        if msg_text and self.room_id:
            payload = json.dumps({"sender": self.username, "message": msg_text})
            self.msg_input.text = ""
            UrlRequest(
                f"{FIREBASE_URL}rooms/{self.room_id}/messages.json",
                req_body=payload,
                method='POST',
                on_success=lambda req, res: self.fetch_messages(0),
                timeout=4
            )

    def fetch_messages(self, dt):
        if not self.room_id:
            return False
        UrlRequest(f"{FIREBASE_URL}rooms/{self.room_id}/messages.json", on_success=self.parse_messages, timeout=3)

    def parse_messages(self, req, result):
        if result:
            for key, val in result.items():
                if key not in self.last_fetched_keys:
                    lbl = Label(
                        text=f"[b]{val['sender']}:[/b] {val['message']}", 
                        markup=True,
                        color=[1, 0.43, 0, 1] if val['sender'] == self.username else [1, 1, 1, 1],
                        size_hint_y=None,
                        height="30dp",
                        halign="left"
                    )
                    lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
                    self.chat_list.add_widget(lbl)
                    self.last_fetched_keys.add(key)

    def leave_room(self):
        Clock.unschedule(self.fetch_messages)
        self.room_id = ""
        self.username = ""
        self.manager.current = 'welcome'

class OrangeChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == "__main__":
    OrangeChatApp().run()
