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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore

FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"
store = JsonStore('orange_chat_local_v4.json')

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.main_layout = BoxLayout(
            orientation='vertical', 
            padding=30, 
            spacing=15, 
            size_hint=(0.88, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))
        
        with self.main_layout.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.bg_card = RoundedRectangle(size=self.main_layout.size, pos=self.main_layout.pos, radius=[16])
        self.main_layout.bind(
            pos=lambda inst, val: setattr(inst, 'bg_card.pos', val),
            size=lambda inst, val: setattr(inst, 'bg_card.size', val)
        )

        title = Label(text="ORANGE CHAT", font_size="28sp", bold=True, color=[1, 0.43, 0, 1], size_hint_y=None, height="40dp")
        self.main_layout.add_widget(title)
        
        self.username_input = TextInput(
            hint_text="Username", multiline=False, padding=[14, 12, 14, 12],
            background_normal='', background_color=[0.18, 0.18, 0.18, 1],
            foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height="48dp"
        )
        self.main_layout.add_widget(self.username_input)

        self.bio_input = TextInput(
            hint_text="Status / Bio", multiline=False, padding=[14, 12, 14, 12],
            background_normal='', background_color=[0.18, 0.18, 0.18, 1],
            foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height="48dp"
        )
        self.main_layout.add_widget(self.bio_input)
        
        save_btn = Button(
            text="ENTER APP", background_normal='', background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1], bold=True, size_hint_y=None, height="50dp", on_release=self.register_profile
        )
        self.main_layout.add_widget(save_btn)
        self.add_widget(self.main_layout)

    def on_enter(self):
        if store.exists('profile'):
            self.manager.current = 'hub'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def register_profile(self, instance):
        username = self.username_input.text.strip().upper()
        bio = self.bio_input.text.strip()
        if username:
            store.put('profile', username=username, bio=bio)
            store.put('rooms', list=[])
            self.manager.current = 'hub'


class ChatHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.06, 0.06, 0.06, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation='vertical')
        
        # Profile Info Card
        self.profile_header = BoxLayout(orientation='vertical', size_hint_y=None, height="85dp", padding=15, spacing=2)
        with self.profile_header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.p_rect = Rectangle(size=self.profile_header.size, pos=self.profile_header.pos)
        self.profile_header.bind(size=self._update_p_rect, pos=self._update_p_rect)
        
        self.profile_name_lbl = Label(text="", font_size="18sp", bold=True, color=[1, 1, 1, 1], halign="left")
        self.profile_name_lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
        self.profile_header.add_widget(self.profile_name_lbl)
        main_layout.add_widget(self.profile_header)
        
        # Create/Join Room Controls
        controls = BoxLayout(orientation='horizontal', size_hint_y=None, height="65dp", padding=10, spacing=10)
        self.room_input = TextInput(
            hint_text="Room ID to Join/Create", multiline=False,
            background_normal='', background_color=[0.15, 0.15, 0.15, 1],
            foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1]
        )
        action_btn = Button(
            text="JOIN", background_normal='', background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1], bold=True, size_hint_x=None, width="80dp", on_release=self.process_room_request
        )
        controls.add_widget(self.room_input)
        controls.add_widget(action_btn)
        main_layout.add_widget(controls)
        
        scroll = ScrollView()
        self.groups_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=15)
        self.groups_list_layout.bind(minimum_height=self.groups_list_layout.setter('height'))
        scroll.add_widget(self.groups_list_layout)
        main_layout.add_widget(scroll)
        
        main_layout.add_widget(Label(text="ORANGE CHAT MULTI-ROOM ENGINE", size_hint_y=None, height="20dp", color=[0.3,0.3,0.3,1], font_size="10sp"))
        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_p_rect(self, instance, value):
        self.p_rect.pos = instance.pos
        self.p_rect.size = instance.size

    def on_pre_enter(self):
        if store.exists('profile'):
            self.profile_name_lbl.text = f"👤 {store.get('profile')['username']}"
        self.refresh_joined_rooms_list()

    def refresh_joined_rooms_list(self):
        self.groups_list_layout.clear_widgets()
        if not store.exists('rooms'): return
        for r_id in store.get('rooms')['list']:
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height="60dp", padding=10)
            with card.canvas.before:
                Color(0.14, 0.14, 0.14, 1)
                card.b_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[8])
            card.bind(pos=lambda inst, val: setattr(inst, 'b_rect.pos', val), size=lambda inst, val: setattr(inst, 'b_rect.size', val))
            
            card.add_widget(Label(text=f"💬 Room: {r_id}", bold=True, halign="left", size_hint_x=0.7))
            open_btn = Button(text="OPEN", background_normal='', background_color=[1, 0.43, 0, 1], bold=True, size_hint_x=0.3, on_release=lambda x, rid=r_id: self.open_room(rid))
            card.add_widget(open_btn)
            self.groups_list_layout.add_widget(card)

    def process_room_request(self, instance):
        room_id = self.room_input.text.strip().upper()
        if room_id:
            self.room_input.text = ""
            current = store.get('rooms')['list'] if store.exists('rooms') else []
            if room_id not in current:
                current.append(room_id)
                store.put('rooms', list=current)
            self.open_room(room_id)

    def open_room(self, room_id):
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_room(store.get('profile')['username'], room_id)
        self.manager.current = 'chat'


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.room_id = ""
        self.last_fetched_keys = set()
        
        with self.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = BoxLayout(orientation='vertical')
        
        # 1. Top Header Bar
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height="55dp", padding=10)
        with header.canvas.before:
            Color(0.14, 0.14, 0.14, 1)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(text="< Hub", size_hint_x=None, width="70dp", background_normal='', background_color=[0,0,0,0], color=[1, 0.43, 0, 1], bold=True, on_release=lambda x: self.leave_room())
        header.add_widget(back_btn)
        self.title_label = Label(text="Room", color=[1, 1, 1, 1], font_size="16sp", bold=True)
        header.add_widget(self.title_label)
        self.layout.add_widget(header)
        
        # 🚀 2. FIXED KEYBOARD DESTRUCTION: INPUT BAR PLACED AT THE TOP!
        # Because it lives at the top of the screen, the keyboard will never reach or cover it.
        input_layout = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height="60dp", spacing=8)
        with input_layout.canvas.before:
            Color(0.11, 0.11, 0.11, 1)
            self.in_rect = Rectangle(size=input_layout.size, pos=input_layout.pos)
        input_layout.bind(size=lambda inst, v: setattr(inst, 'in_rect.size', v), pos=lambda inst, v: setattr(inst, 'in_rect.pos', v))

        self.msg_input = TextInput(
            hint_text="Type message here...  😀 🔥", multiline=False,
            background_normal='', background_color=[0.18, 0.18, 0.18, 1],
            foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], padding=[12, 10, 12, 10]
        )
        send_btn = Button(
            text="SEND", size_hint_x=None, width="75dp",
            background_normal='', background_color=[1, 0.43, 0, 1], color=[1, 1, 1, 1], bold=True,
            on_release=self.send_message
        )
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(send_btn)
        self.layout.add_widget(input_layout)
        
        # 3. Message Stream area (Fills the lower half)
        scroll = ScrollView()
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=12)
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        scroll.add_widget(self.chat_list)
        self.layout.add_widget(scroll)
        
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def setup_room(self, username, room_id):
        self.username = username
        self.room_id = room_id
        self.title_label.text = f"👥 Room: {room_id}"
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
                req_body=payload, method='POST',
                on_success=lambda req, res: self.fetch_messages(0),
                timeout=4
            )

    def fetch_messages(self, dt):
        if not self.room_id: return False
        UrlRequest(f"{FIREBASE_URL}rooms/{self.room_id}/messages.json", on_success=self.parse_messages, timeout=3)

    def parse_messages(self, req, result):
        if result and self.room_id:
            for key, val in result.items():
                if key not in self.last_fetched_keys:
                    is_me = val['sender'].strip().upper() == self.username.strip().upper()
                    display_text = f"[b]{val['sender']}:[/b] {val['message']}"
                    
                    row_box = BoxLayout(size_hint_y=None, height="45dp")
                    bubble_card = BoxLayout(size_hint_y=1, padding=[12, 6, 12, 6], size_hint_x=0.75)
                    
                    lbl = Label(text=display_text, markup=True, font_size="14sp", color=[1, 1, 1, 1], halign="left", valign="middle")
                    lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
                    bubble_card.add_widget(lbl)
                    
                    if is_me:
                        row_box.padding = [50, 2, 5, 2]
                        row_box.pos_hint = {"right": 1.0}
                        card_color = [1, 0.43, 0, 0.95] # Orange right
                    else:
                        row_box.padding = [5, 2, 50, 2]
                        row_box.pos_hint = {"left": 1.0}
                        card_color = [0.16, 0.16, 0.16, 1] # Dark Left

                    with bubble_card.canvas.before:
                        Color(*card_color)
                        bubble_card.bg_shape = RoundedRectangle(size=bubble_card.size, pos=bubble_card.pos, radius=[10])
                    bubble_card.bind(pos=lambda inst, v: setattr(inst, 'bg_shape.pos', v), size=lambda inst, v: setattr(inst, 'bg_shape.size', v))
                    
                    row_box.add_widget(bubble_card)
                    # Insert new messages right at the top of the stream so they are immediately visible!
                    self.chat_list.add_widget(row_box, index=len(self.chat_list.children))
                    self.last_fetched_keys.add(key)

    def leave_room(self):
        Clock.unschedule(self.fetch_messages)
        self.room_id = ""
        self.manager.current = 'hub'


class OrangeChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ChatHubScreen(name='hub'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == "__main__":
    OrangeChatApp().run()
