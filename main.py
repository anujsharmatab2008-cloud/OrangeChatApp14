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

# Production Windows & Layout Adjustments
Window.softinput_mode = 'resize'
FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"

# Local Storage to remember joined rooms and profile details permanently
store = JsonStore('orange_chat_local.json')

class WelcomeScreen(Screen):
    """
    Initial Setup Screen for users to create their global cloud profile
    before entering the primary multi-room application engine.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1) # Pitch premium dark theme background
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.main_layout = BoxLayout(
            orientation='vertical', 
            padding=40, 
            spacing=20, 
            size_hint=(0.9, 0.75), 
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        title = Label(
            text="ORANGE CHAT", 
            font_size="36sp", 
            bold=True,
            color=[1, 0.43, 0, 1],
            size_hint_y=None,
            height="60dp"
        )
        self.main_layout.add_widget(title)
        
        subtitle = Label(
            text="Set up your global network profile identity",
            color=[0.6, 0.6, 0.6, 1],
            font_size="14sp",
            size_hint_y=None,
            height="20dp"
        )
        self.main_layout.add_widget(subtitle)
        
        self.username_input = TextInput(
            hint_text="Create Unique Username",
            multiline=False,
            padding=[15, 15, 15, 15],
            background_color=[0.12, 0.12, 0.12, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height="52dp"
        )
        self.main_layout.add_widget(self.username_input)

        self.bio_input = TextInput(
            hint_text="Status/Bio (e.g., Active 🚀)",
            multiline=False,
            padding=[15, 15, 15, 15],
            background_color=[0.12, 0.12, 0.12, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height="52dp"
        )
        self.main_layout.add_widget(self.bio_input)
        
        save_btn = Button(
            text="CREATE ACCOUNT & ENTER",
            background_normal='',
            background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1],
            bold=True,
            size_hint_y=None,
            height="55dp",
            on_release=self.register_profile
        )
        self.main_layout.add_widget(save_btn)
        
        self.status_label = Label(text="", color=[1, 0.43, 0, 1], size_hint_y=None, height="30dp")
        self.main_layout.add_widget(self.status_label)
        
        self.add_widget(self.main_layout)
        Window.bind(on_keyboard_height=self.adjust_for_keyboard)

    def on_enter(self):
        # Auto-bypass registration if profile details already exist locally
        if store.exists('profile'):
            Clock.schedule_once(lambda dt: self.bypass_welcome(), 0.1)

    def bypass_welcome(self):
        self.manager.current = 'hub'

    def adjust_for_keyboard(self, window, height):
        if height > 0:
            self.main_layout.pos_hint = {"center_x": 0.5, "center_y": 0.7}
        else:
            self.main_layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def register_profile(self, instance):
        username = self.username_input.text.strip().upper()
        bio = self.bio_input.text.strip()
        if not username or len(username) < 3:
            self.status_label.text = "Username must be at least 3 letters!"
            return
        
        self.status_label.text = "Syncing cloud configurations..."
        profile_payload = json.dumps({"username": username, "bio": bio})
        
        UrlRequest(
            f"{FIREBASE_URL}users/{username}.json",
            req_body=profile_payload,
            method='PUT',
            on_success=lambda req, res: self.on_register_success(username, bio),
            timeout=4
        )

    def on_register_success(self, username, bio):
        store.put('profile', username=username, bio=bio)
        if not store.exists('rooms'):
            store.put('rooms', list=[])
        self.manager.current = 'hub'


class ChatHubScreen(Screen):
    """
    The main Dashboard screen engineered identically to modern communication apps.
    Allows viewing profile summary, list of joined groups, and creation of new channels.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation='vertical')
        
        # Profile Details Top Header Card Block
        self.profile_header = BoxLayout(orientation='vertical', size_hint_y=None, height="100dp", padding=15, spacing=5)
        with self.profile_header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.p_rect = Rectangle(size=self.profile_header.size, pos=self.profile_header.pos)
        self.profile_header.bind(size=self._update_p_rect, pos=self._update_p_rect)
        
        self.profile_name_lbl = Label(text="Username: --", font_size="20sp", bold=True, color=[1, 0.43, 0, 1], halign="left")
        self.profile_name_lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
        self.profile_bio_lbl = Label(text="Bio: --", font_size="13sp", color=[0.6, 0.6, 0.6, 1], halign="left")
        self.profile_bio_lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
        
        self.profile_header.add_widget(self.profile_name_lbl)
        self.profile_header.add_widget(self.profile_bio_lbl)
        main_layout.add_widget(self.profile_header)
        
        # Room Controls Panel
        controls = BoxLayout(orientation='horizontal', size_hint_y=None, height="60dp", padding=10, spacing=10)
        self.room_input = TextInput(
            hint_text="Room ID to Join/Create", multiline=False,
            background_color=[0.16, 0.16, 0.16, 1], foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.5, 0.5, 0.5, 1], padding=[10, 10, 10, 10]
        )
        action_btn = Button(
            text="ENTER GROUP", background_normal='', background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1], bold=True, size_hint_x=None, width="130dp", on_release=self.process_room_request
        )
        controls.add_widget(self.room_input)
        controls.add_widget(action_btn)
        main_layout.add_widget(controls)
        
        # Section Header Title
        section_title = Label(text="  MY CHATS & ACTIVE GROUPS", font_size="13sp", bold=True, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="30dp", halign="left")
        section_title.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
        main_layout.add_widget(section_title)

        # Dynamic Scrolling List consisting of all distinct group rooms joined
        scroll = ScrollView()
        self.groups_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        self.groups_list_layout.bind(minimum_height=self.groups_list_layout.setter('height'))
        scroll.add_widget(self.groups_list_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_p_rect(self, instance, value):
        self.p_rect.pos = instance.pos
        self.p_rect.size = instance.size

    def on_pre_enter(self):
        # Read parameters from data schemas to dynamically refresh dashboard interface metrics
        if store.exists('profile'):
            p = store.get('profile')
            self.profile_name_lbl.text = f"👤 {p['username']}"
            self.profile_bio_lbl.text = f"✨ Status: {p['bio'] if p['bio'] else 'Available'}"
        self.refresh_joined_rooms_list()

    def refresh_joined_rooms_list(self):
        self.groups_list_layout.clear_widgets()
        if not store.exists('rooms'):
            return
            
        joined_list = store.get('rooms')['list']
        for r_id in joined_list:
            # Generate Premium UI Chat Cards for every group link references
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height="65dp", padding=10, spacing=15)
            with card.canvas.before:
                Color(0.14, 0.14, 0.14, 1)
                card.b_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[10, 10, 10, 10])
            card.bind(
                pos=lambda instance, val: setattr(instance, 'b_rect.pos', val),
                size=lambda instance, val: setattr(instance, 'b_rect.size', val)
            )
            
            meta_box = BoxLayout(orientation='vertical', spacing=2)
            room_title = Label(text=f"💬 Group Channel: {r_id}", font_size="16sp", bold=True, color=[1, 1, 1, 1], halign="left")
            room_title.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
            room_subtitle = Label(text="Tap to instantly resume messages panel", font_size="12sp", color=[0.5, 0.5, 0.5, 1], halign="left")
            room_subtitle.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
            
            meta_box.add_widget(room_title)
            meta_box.add_widget(room_subtitle)
            card.add_widget(meta_box)
            
            open_btn = Button(
                text="OPEN", background_normal='', background_color=[1, 0.43, 0, 0.15],
                color=[1, 0.43, 0, 1], bold=True, size_hint_x=None, width="70dp",
                on_release=lambda x, rid=r_id: self.open_group_channel(rid)
            )
            card.add_widget(open_btn)
            self.groups_list_layout.add_widget(card)

    def process_room_request(self, instance):
        room_id = self.room_input.text.strip().upper()
        if not room_id or len(room_id) < 3:
            return
            
        self.room_input.text = ""
        current_list = store.get('rooms')['list'] if store.exists('rooms') else []
        
        if room_id not in current_list:
            current_list.append(room_id)
            store.put('rooms', list=current_list)
            
        # Register a quick root base on Firebase Realtime nodes to secure data channels safely
        initial_payload = json.dumps({"created_by": store.get('profile')['username'], "initialized": True})
        UrlRequest(f"{FIREBASE_URL}rooms/{room_id}/meta.json", req_body=initial_payload, method='PUT')
        
        self.open_group_channel(room_id)

    def open_group_channel(self, room_id):
        username = store.get('profile')['username']
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_room(username, room_id)
        self.manager.current = 'chat'


class ChatScreen(Screen):
    """
    Polished Communication Workspace Panel housing real-time parsing workflows,
    distinct message bubble arrays, and integrated multi-lingual emoji injection layout.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.room_id = ""
        self.last_fetched_keys = set()
        
        with self.canvas.before:
            Color(0.06, 0.06, 0.06, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = BoxLayout(orientation='vertical')
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height="60dp", padding=10)
        with header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(
            text="< Dashboard", 
            size_hint_x=None, width="110dp",
            background_normal='', background_color=[0, 0, 0, 0],
            color=[1, 0.43, 0, 1], bold=True,
            on_release=lambda x: self.leave_room()
        )
        header.add_widget(back_btn)
        
        self.title_label = Label(text="Room: ----", color=[1, 1, 1, 1], font_size="18sp", bold=True)
        header.add_widget(self.title_label)
        self.layout.add_widget(header)
        
        scroll = ScrollView()
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=12)
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        scroll.add_widget(self.chat_list)
        self.layout.add_widget(scroll)
        
        input_layout = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height="65dp", spacing=10)
        self.msg_input = TextInput(
            hint_text="Type message or paste emoji...",
            multiline=False,
            background_color=[0.14, 0.14, 0.14, 1],
            foreground_color=[1, 1, 1, 1],
            hint_text_color=[0.5, 0.5, 0.5, 1],
            padding=[12, 12, 12, 12]
        )
        send_btn = Button(
            text="SEND", 
            size_hint_x=None, width="85dp",
            background_normal='', background_color=[1, 0.43, 0, 1],
            color=[1, 1, 1, 1], bold=True,
            on_release=self.send_message
        )
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(send_btn)
        self.layout.add_widget(input_layout)
        
        self.add_widget(self.layout)
        Window.bind(on_keyboard_height=self.adjust_chat_layout)

    def adjust_chat_layout(self, window, height):
        if height > 0:
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
        self.title_label.text = f"👥 {room_id}"
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
        if result and self.room_id:
            for key, val in result.items():
                if key not in self.last_fetched_keys:
                    is_me = val['sender'].strip().upper() == self.username.strip().upper()
                    
                    # Core Layout Alignment Strategy for Play Store Standards
                    bubble_wrapper = BoxLayout(
                        size_hint_y=None, 
                        height="60dp", 
                        padding=[5, 2, 5, 2]
                    )
                    
                    # Structural Offset Placement: Left side vs Right side
                    if is_me:
                        bubble_wrapper.padding = [60, 2, 10, 2] # Push firmly to the right side
                        card_color = [1, 0.43, 0, 0.9] # Bright iconic Orange branding
                        text_theme = [1, 1, 1, 1]
                    else:
                        bubble_wrapper.padding = [10, 2, 60, 2] # Push firmly to the left side
                        card_color = [0.15, 0.15, 0.15, 1] # Dark WhatsApp slate gray container
                        text_theme = [0.9, 0.9, 0.9, 1]

                    with bubble_wrapper.canvas.before:
                        Color(*card_color)
                        bubble_wrapper.bg_shape = RoundedRectangle(
                            size=bubble_wrapper.size, pos=bubble_wrapper.pos,
                            radius=[14, 14, 2, 14] if is_me else [14, 14, 14, 2]
                        )
                    bubble_wrapper.bind(
                        pos=lambda instance, v: setattr(instance, 'bg_shape.pos', v),
                        size=lambda instance, v: setattr(instance, 'bg_shape.size', v)
                    )
                    
                    lbl = Label(
                        text=f"[b]{val['sender']}:[/b] {val['message']}", 
                        markup=True,
                        color=text_theme,
                        font_size="15sp",
                        halign="left",
                        valign="center"
                    )
                    lbl.bind(width=lambda idx, w: setattr(idx, 'text_size', (w, None)))
                    
                    bubble_wrapper.add_widget(lbl)
                    self.chat_list.add_widget(bubble_wrapper)
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
