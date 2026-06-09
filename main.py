import random
import string
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
import requests

# ⚠️ PASTE YOUR FIREBASE URL HERE
FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"

class WelcomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Center container layout
        main_layout = MDBoxLayout(orientation='vertical', padding=30, spacing=20, size_hint=(0.9, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        # Title
        title = MDLabel(
            text="ORANGE CHAT", 
            font_style="H4", 
            halign="center", 
            theme_text_color="Custom", 
            text_color=[1, 0.43, 0, 1] # Orange
        )
        main_layout.add_widget(title)
        
        # Username Input
        self.username_input = MDTextField(
            hint_text="Enter your Username",
            mode="round",
            line_color_focus=[1, 0.43, 0, 1],
            hint_text_color_focus=[1, 0.43, 0, 1]
        )
        main_layout.add_widget(self.username_input)
        
        # Room ID Input (For joining)
        self.room_input = MDTextField(
            hint_text="Enter Room ID (To Join)",
            mode="round",
            line_color_focus=[1, 0.43, 0, 1],
            hint_text_color_focus=[1, 0.43, 0, 1]
        )
        main_layout.add_widget(self.room_input)
        
        # Action Buttons Layout
        btn_layout = MDBoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height="50dp")
        
        join_btn = MDRaisedButton(
            text="Join Room",
            md_bg_color=[1, 0.43, 0, 1],
            text_color=[1, 1, 1, 1],
            on_release=self.join_room
        )
        
        create_btn = MDRaisedButton(
            text="Create New Room",
            md_bg_color=[0.2, 0.2, 0.2, 1],
            text_color=[1, 0.43, 0, 1],
            on_release=self.create_room
        )
        
        btn_layout.add_widget(join_btn)
        btn_layout.add_widget(create_btn)
        main_layout.add_widget(btn_layout)
        
        # Error / Status Label
        self.status_label = MDLabel(text="", halign="center", theme_text_color="Error")
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)

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
            try:
                response = requests.get(f"{FIREBASE_URL}rooms/{room_id}.json", timeout=5)
                if response.status_code == 200 and response.json() is not None:
                    self.switch_to_chat(username, room_id)
                else:
                    self.status_label.text = "Room ID does not exist!"
            except Exception:
                self.status_label.text = "Connection Error!"

    def create_room(self, instance):
        username = self.get_user_details()
        if username:
            room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            initial_data = {"created_by": username, "messages": ""}
            try:
                requests.put(f"{FIREBASE_URL}rooms/{room_id}.json", json=initial_data, timeout=5)
                self.switch_to_chat(username, room_id)
            except Exception:
                self.status_label.text = "Failed to create room!"

    def switch_to_chat(self, username, room_id):
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_room(username, room_id)
        self.manager.current = 'chat'


class ChatScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.room_id = ""
        self.last_fetched_keys = set()
        
        # Main Layout
        layout = MDBoxLayout(orientation='vertical')
        
        # 1. Top App Bar (FIXED: anchor_title removed to prevent crash)
        self.toolbar = MDTopAppBar(title="Room: ----")
        self.toolbar.md_bg_color = [0.07, 0.07, 0.07, 1] 
        self.toolbar.specific_text_color = [1, 0.43, 0, 1]
        self.toolbar.left_action_items = [["arrow-left", lambda x: self.leave_room()]]
        layout.add_widget(self.toolbar)
        
        # 2. Chat History Area
        scroll = ScrollView()
        self.chat_list = MDList()
        scroll.add_widget(self.chat_list)
        layout.add_widget(scroll)
        
        # 3. Input Message Area Layout
        input_layout = MDBoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height="60dp")
        
        self.msg_input = MDTextField(
            hint_text="Type a message...",
            mode="round",
            line_color_focus=[1, 0.43, 0, 1],
            hint_text_color_focus=[1, 0.43, 0, 1]
        )
        
        send_btn = MDIconButton(
            icon="send",
            theme_icon_color="Custom",
            icon_color=[1, 0.43, 0, 1],
            on_release=self.send_message
        )
        
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(send_btn)
        layout.add_widget(input_layout)
        
        layout.add_widget(input_layout)
        self.add_widget(layout)

    def setup_room(self, username, room_id):
        self.username = username
        self.room_id = room_id
        self.toolbar.title = f"Room ID: {room_id}"
        self.chat_list.clear_widgets()
        self.last_fetched_keys.clear()
        
        Clock.schedule_interval(self.fetch_messages, 1.5)

    def send_message(self, instance):
        msg_text = self.msg_input.text.strip()
        if msg_text and self.room_id:
            payload = {"sender": self.username, "message": msg_text}
            try:
                requests.post(f"{FIREBASE_URL}rooms/{self.room_id}/messages.json", json=payload, timeout=5)
                self.msg_input.text = ""
                self.fetch_messages(0)
            except Exception as e:
                print("Failed to send:", e)

    def fetch_messages(self, dt):
        if not self.room_id:
            return False
            
        try:
            response = requests.get(f"{FIREBASE_URL}rooms/{self.room_id}/messages.json", timeout=3)
            if response.status_code == 200 and response.json():
                messages = response.json()
                
                for key, val in messages.items():
                    if key not in self.last_fetched_keys:
                        display_text = f"{val['sender']}: {val['message']}"
                        text_color = [1, 0.43, 0, 1] if val['sender'] == self.username else [1, 1, 1, 1]
                        
                        item = OneLineListItem(text=display_text, theme_text_color="Custom", text_color=text_color)
                        self.chat_list.add_widget(item)
                        self.last_fetched_keys.add(key)
        except Exception as e:
            print("Error updating chat stream:", e)

    def leave_room(self):
        Clock.unschedule(self.fetch_messages)
        self.room_id = ""
        self.username = ""
        self.manager.current = 'welcome'


class DiscordStyleChatApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == "__main__":
    DiscordStyleChatApp().run()
