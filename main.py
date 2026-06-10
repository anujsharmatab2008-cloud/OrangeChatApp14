import random
import string
import json
import sys

# 1. THE CRASH MONITOR: Captures startup blocks and displays them instantly
try:
    from kivy.clock import Clock
    from kivy.uix.screenmanager import ScreenManager
    from kivy.uix.scrollview import ScrollView
    from kivy.network.urlrequest import UrlRequest
    from kivymd.app import MDApp
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.button import MDIconButton, MDRaisedButton
    from kivymd.uix.label import MDLabel
    from kivymd.uix.list import MDList, OneLineListItem
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.textfield import MDTextField
except Exception as startup_error:
    # If a mobile library fails to load, force Android to show it instead of going black
    from kivy.app import App
    from kivy.uix.label import Label
    class CrashApp(App):
        def build(self):
            return Label(text=f"CRITICAL BOOT ERROR:\n{str(startup_error)}", halign="center")
    if __name__ == "__main__":
        CrashApp().run()
        sys.exit()

# ⚠️ Your Firebase Realtime Database Endpoint URL
FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"

class WelcomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = MDBoxLayout(
            orientation='vertical', 
            padding=30, 
            spacing=20, 
            size_hint=(0.9, 0.8), 
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        title = MDLabel(
            text="ORANGE CHAT", 
            font_style="H4", 
            halign="center", 
            theme_text_color="Custom", 
            text_color=[1, 0.43, 0, 1]
        )
        main_layout.add_widget(title)
        
        self.username_input = MDTextField(
            hint_text="Enter your Username",
            mode="round",
            line_color_focus=[1, 0.43, 0, 1],
            hint_text_color_focus=[1, 0.43, 0, 1]
        )
        main_layout.add_widget(self.username_input)
        
        self.room_input = MDTextField(
            hint_text="Enter Room ID (To Join)",
            mode="round",
            line_color_focus=[1, 0.43, 0, 1],
            hint_text_color_focus=[1, 0.43, 0, 1]
        )
        main_layout.add_widget(self.room_input)
        
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
            self.status_label.text = "Connecting..."
            UrlRequest(
                f"{FIREBASE_URL}rooms/{room_id}.json",
                on_success=lambda req, res: self.on_join_success(res, username, room_id),
                on_failure=self.on_net_error,
                on_error=self.on_net_error,
                timeout=5
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
                timeout=5
            )

    def on_net_error(self, req, error):
        self.status_label.text = "Connection/Server Error!"

    def switch_to_chat(self, username, room_id):
        self.status_label.text = ""
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_room(username, room_id)
        self.manager.current = 'chat'


class ChatScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.room_id = ""
        self.last_fetched_keys = set()
        
        layout = MDBoxLayout(orientation='vertical')
        
        header = MDBoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height="56dp", 
            md_bg_color=[0.07, 0.07, 0.07, 1], 
            padding=[5, 0, 5, 0],
            spacing=10
        )
        
        back_btn = MDIconButton(
            icon="arrow-left", 
            theme_icon_color="Custom", 
            icon_color=[1, 0.43, 0, 1],
            on_release=lambda x: self.leave_room()
        )
        header.add_widget(back_btn)
        
        self.title_label = MDLabel(
            text="Room: ----", 
            theme_text_color="Custom", 
            text_color=[1, 0.43, 0, 1],
            valign="middle"
        )
        header.add_widget(self.title_label)
        layout.add_widget(header)
        
        scroll = ScrollView()
        self.chat_list = MDList()
        scroll.add_widget(self.chat_list)
        layout.add_widget(scroll)
        
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
        
        self.add_widget(layout)

    def setup_room(self, username, room_id):
        self.username = username
        self.room_id = room_id
        self.title_label.text = f"Room ID: {room_id}"
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
                timeout=5
            )

    def fetch_messages(self, dt):
        if not self.room_id:
            return False
            
        UrlRequest(
            f"{FIREBASE_URL}rooms/{self.room_id}/messages.json",
            on_success=self.parse_messages,
            timeout=3
        )

    def parse_messages(self, req, result):
        if result:
            for key, val in result.items():
                if key not in self.last_fetched_keys:
                    display_text = f"{val['sender']}: {val['message']}"
                    text_color = [1, 0.43, 0, 1] if val['sender'] == self.username else [1, 1, 1, 1]
                    
                    item = OneLineListItem(text=display_text, theme_text_color="Custom", text_color=text_color)
                    self.chat_list.add_widget(item)
                    self.last_fetched_keys.add(key)

    def leave_room(self):
        Clock.unschedule(self.fetch_messages)
        self.room_id = ""
        self.username = ""
        self.manager.current = 'welcome'


class DiscordStyleChatApp(MDApp):
    def build(self):
        try:
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Orange"
            
            sm = ScreenManager()
            sm.add_widget(WelcomeScreen(name='welcome'))
            sm.add_widget(ChatScreen(name='chat'))
            return sm
        except Exception as ui_error:
            # 2. RENDER CRASH PROTECTION: If KivyMD styles fail, catch it visually
            from kivy.uix.label import Label
            return Label(text=f"UI CONFIGURATION ERROR:\n{str(ui_error)}", halign="center")

if __name__ == "__main__":
    try:
        DiscordStyleChatApp().run()
    except Exception as run_error:
        from kivy.app import App
        from kivy.uix.label import Label
        class EmergencyApp(App):
            def build(self):
                return Label(text=f"RUNTIME ENGINE ERROR:\n{str(run_error)}", halign="center")
        EmergencyApp().run()
