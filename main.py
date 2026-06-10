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

# Core System Window Rules
Window.softinput_mode = 'resize'
FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"
store = JsonStore('orange_chat_local_v8.json')

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        outer_layout = BoxLayout(orientation='vertical', padding=[20, 40, 20, 20])
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=15, size_hint=(0.92, None), pos_hint={"center_x": 0.5})
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))
        
        with self.main_layout.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.bg_card = RoundedRectangle(size=self.main_layout.size, pos=self.main_layout.pos, radius=[16])
        self.main_layout.bind(pos=lambda inst, val: setattr(inst, 'bg_card.pos', val), size=lambda inst, val: setattr(inst, 'bg_card.size', val))

        title = Label(text="ORANGE CHAT", font_size="28sp", bold=True, color=[1, 0.43, 0, 1], size_hint_y=None, height="40dp")
        self.main_layout.add_widget(title)
        
        self.username_input = TextInput(hint_text="Create Unique Username ID", multiline=False, padding=[14, 12, 14, 12], background_normal='', background_color=[0.18, 0.18, 0.18, 1], foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height="48dp")
        self.main_layout.add_widget(self.username_input)

        self.bio_input = TextInput(hint_text="Bio Status", multiline=False, padding=[14, 12, 14, 12], background_normal='', background_color=[0.18, 0.18, 0.18, 1], foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height="48dp")
        self.main_layout.add_widget(self.bio_input)
        
        save_btn = Button(text="REGISTER ACCOUNT", background_normal='', background_color=[1, 0.43, 0, 1], color=[1, 1, 1, 1], bold=True, size_hint_y=None, height="50dp", on_release=self.register_profile)
        self.main_layout.add_widget(save_btn)
        
        outer_layout.add_widget(BoxLayout(size_hint_y=0.1))
        outer_layout.add_widget(self.main_layout)
        outer_layout.add_widget(BoxLayout(size_hint_y=0.6))
        
        copyright_lbl = Label(text="© 2026 Anuj Sharma. Managed and Developed by Anuj Sharma.", font_size="11sp", color=[0.4, 0.4, 0.4, 1], size_hint_y=None, height="30dp", halign="center")
        outer_layout.add_widget(copyright_lbl)
        self.add_widget(outer_layout)

    def on_enter(self):
        if store.exists('profile'):
            self.manager.current = 'hub'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def register_profile(self, instance):
        username = self.username_input.text.strip().upper().replace(" ", "_")
        bio = self.bio_input.text.strip()
        if username:
            payload = json.dumps({"username": username, "bio": bio})
            UrlRequest(f"{FIREBASE_URL}users/{username}.json", req_body=payload, method='PUT', on_success=lambda r, res: self.save_local(username, bio))

    def save_local(self, username, bio):
        store.put('profile', username=username, bio=bio)
        self.manager.current = 'hub'


class ChatHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.06, 0.06, 0.06, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.main_layout = BoxLayout(orientation='vertical')
        
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height="70dp", padding=12)
        with self.header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.h_rect = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(size=self._update_h_rect, pos=self._update_h_rect)
        
        self.profile_lbl = Label(text="👤 ORANGE SOCIAL", font_size="16sp", bold=True, color=[1,1,1,1], halign="left")
        self.header.add_widget(self.profile_lbl)
        
        search_trigger_btn = Button(text="🔍 EXPLORE", size_hint_x=None, width="100dp", background_normal='', background_color=[1, 0.43, 0, 1], bold=True, on_release=self.go_to_explore)
        self.header.add_widget(search_trigger_btn)
        self.main_layout.add_widget(self.header)

        # Tabs for Direct Messages vs. Group Channels
        tabs = BoxLayout(orientation='horizontal', size_hint_y=None, height="45dp")
        dm_tab = Button(text="DIRECT MESSAGES", background_normal='', background_color=[0.15, 0.15, 0.15, 1], color=[1,1,1,1], bold=True, on_release=lambda x: self.load_chats_view("dm"))
        gp_tab = Button(text="GROUPS", background_normal='', background_color=[0.2, 0.2, 0.2, 1], color=[1, 0.43, 0, 1], bold=True, on_release=lambda x: self.load_chats_view("group"))
        tabs.add_widget(dm_tab)
        tabs.add_widget(gp_tab)
        self.main_layout.add_widget(tabs)
        
        scroll = ScrollView()
        self.feed_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=12)
        self.feed_layout.bind(minimum_height=self.feed_layout.setter('height'))
        scroll.add_widget(self.feed_layout)
        self.main_layout.add_widget(scroll)
        
        self.add_widget(self.main_layout)

    def _update_rect(self, instance, value): self.rect.pos = instance.pos; self.rect.size = instance.size
    def _update_h_rect(self, instance, value): self.h_rect.pos = instance.pos; self.h_rect.size = instance.size

    def on_pre_enter(self):
        if store.exists('profile'):
            self.my_id = store.get('profile')['username']
            self.profile_lbl.text = f"👤 {self.my_id}"
            self.load_chats_view("dm")

    def go_to_explore(self, instance):
        self.manager.current = 'explore'

    def load_chats_view(self, mode):
        self.feed_layout.clear_widgets()
        if mode == "group":
            create_gp_box = BoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing=5)
            self.gp_name_in = TextInput(hint_text="Group Name...", multiline=False, background_color=[0.15,0.15,0.15,1], foreground_color=[1,1,1,1])
            make_btn = Button(text="CREATE", size_hint_x=None, width="80dp", background_color=[1,0.43,0,1], on_release=self.fire_group_creation)
            create_gp_box.add_widget(self.gp_name_in)
            create_gp_box.add_widget(make_btn)
            self.feed_layout.add_widget(create_gp_box)
            
        UrlRequest(f"{FIREBASE_URL}chats.json", on_success=lambda req, res: self.populate_active_feed(res, mode))

    def fire_group_creation(self, instance):
        gp_name = self.gp_name_in.text.strip().upper().replace(" ", "_")
        if gp_name:
            self.gp_name_in.text = ""
            chat_screen = self.manager.get_screen('chat')
            chat_screen.setup_chat_room(f"GP_{gp_name}", is_group=True)
            self.manager.current = 'chat'

    def populate_active_feed(self, result, mode):
        if not result: return
        for chat_id, data in result.items():
            if mode == "group" and chat_id.startswith("GP_"):
                self.add_feed_row(chat_id, chat_id.replace("GP_", "👥 GROUP: "))
            elif mode == "dm" and not chat_id.startswith("GP_") and self.my_id in chat_id:
                receiver = chat_id.replace(self.my_id, "").replace("_AND_", "")
                self.add_feed_row(chat_id, f"💬 CHAT: {receiver}")

    def add_feed_row(self, target_id, label_text):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height="55dp", padding=6)
        with row.canvas.before:
            Color(0.14, 0.14, 0.14, 1)
            row.r_shape = RoundedRectangle(size=row.size, pos=row.pos, radius=[8])
        row.bind(pos=lambda inst, v: setattr(inst, 'r_shape.pos', v), size=lambda inst, v: setattr(inst, 'r_shape.size', v))
        
        row.add_widget(Label(text=label_text, bold=True, halign="left"))
        open_btn = Button(text="OPEN", size_hint_x=None, width="75dp", background_normal='', background_color=[1, 0.43, 0, 1], bold=True, on_release=lambda x: self.open_conversation(target_id, mode_group=target_id.startswith("GP_")))
        row.add_widget(open_btn)
        self.feed_layout.add_widget(row)

    def open_conversation(self, chat_id, mode_group):
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_chat_room(chat_id, is_group=mode_group)
        self.manager.current = 'chat'


class ExploreSocialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')
        
        nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height="55dp", padding=10)
        back_btn = Button(text="< BACK", size_hint_x=None, width="80dp", background_color=[0,0,0,0], color=[1,0.43,0,1], bold=True, on_release=self.go_back)
        nav_bar.add_widget(back_btn)
        nav_bar.add_widget(Label(text="EXPLORE DIRECTORY", bold=True, font_size="16sp"))
        layout.add_widget(nav_bar)

        search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height="55dp", padding=10, spacing=8)
        self.search_input = TextInput(hint_text="Search Username...", multiline=False, background_color=[0.15,0.15,0.15,1], foreground_color=[1,1,1,1], hint_text_color=[0.4,0.4,0.4,1])
        run_search_btn = Button(text="SEARCH", size_hint_x=None, width="85dp", background_color=[1,0.43,0,1], bold=True, on_release=self.search_user_id)
        search_box.add_widget(self.search_input)
        search_box.add_widget(run_search_btn)
        layout.add_widget(search_box)

        scroll = ScrollView()
        self.results_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=15)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll.add_widget(self.results_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def _update_rect(self, instance, value): self.rect.pos = instance.pos; self.rect.size = instance.size
    def go_back(self, instance): self.manager.current = 'hub'

    def search_user_id(self, instance):
        self.results_layout.clear_widgets()
        query = self.search_input.text.strip().upper()
        if query:
            UrlRequest(f"{FIREBASE_URL}users/{query}.json", on_success=self.display_searched_user)

    def display_searched_user(self, req, res):
        if not res:
            self.results_layout.add_widget(Label(text="User profile not found.", color=[0.5,0.5,0.5,1]))
            return
        
        my_id = store.get('profile')['username']
        target_username = res['username']
        if target_username == my_id: return

        card = BoxLayout(orientation='horizontal', size_hint_y=None, height="65dp", padding=10)
        with card.canvas.before:
            Color(0.13, 0.13, 0.13, 1)
            card.bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[8])
        card.bind(pos=lambda inst, v: setattr(inst, 'bg.pos', v), size=lambda inst, v: setattr(inst, 'bg.size', v))
        
        card.add_widget(Label(text=f"👤 {target_username}\n[size=12sp]{res.get('bio','')}[/size]", markup=True, halign="left"))
        
        connect_btn = Button(text="CHAT", size_hint_x=None, width="100dp", background_color=[1,0.43,0,1], bold=True, 
                            on_release=lambda x: self.open_direct_message(my_id, target_username))
        card.add_widget(connect_btn)
        self.results_layout.add_widget(card)

    def open_direct_message(self, my_id, target_id):
        # Alphabetically sorted unique DM thread string
        dm_room_id = f"{my_id}_AND_{target_id}" if my_id < target_id else f"{target_id}_AND_{my_id}"
        payload = json.dumps({"active": True})
        UrlRequest(f"{FIREBASE_URL}chats/{dm_room_id}/meta.json", req_body=payload, method='PUT',
                   on_success=lambda r, re: self.open_instantly(dm_room_id))

    def open_instantly(self, room_id):
        chat_screen = self.manager.get_screen('chat')
        chat_screen.setup_chat_room(room_id, is_group=False)
        self.manager.current = 'chat'


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.chat_id = ""
        self.last_fetched_keys = set()
        
        with self.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = BoxLayout(orientation='vertical')
        
        # 1. FIXED TOP NAVIGATION HEADER
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height="55dp", padding=10)
        with header.canvas.before:
            Color(0.14, 0.14, 0.14, 1)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(text="< LEAVE", size_hint_x=None, width="80dp", background_normal='', background_color=[0,0,0,0], color=[1, 0.43, 0, 1], bold=True, on_release=lambda x: self.leave_chat())
        header.add_widget(back_btn)
        self.title_label = Label(text="Secure Workspace", color=[1, 1, 1, 1], font_size="15sp", bold=True)
        header.add_widget(self.title_label)
        self.layout.add_widget(header)
        
        # 2. ANTI-KEYBOARD BLOCKING PANEL (TOP ADJUSTMENT)
        input_layout = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height="60dp", spacing=8)
        with input_layout.canvas.before:
            Color(0.11, 0.11, 0.11, 1)
            self.in_rect = Rectangle(size=input_layout.size, pos=input_layout.pos)
        input_layout.bind(size=lambda inst, v: setattr(inst, 'in_rect.size', v), pos=lambda inst, v: setattr(inst, 'in_rect.pos', v))

        self.msg_input = TextInput(hint_text="Write your text message here...", multiline=False, background_normal='', background_color=[0.18, 0.18, 0.18, 1], foreground_color=[1, 1, 1, 1], hint_text_color=[0.4, 0.4, 0.4, 1], padding=[12, 10, 12, 10])
        send_btn = Button(text="SEND", size_hint_x=None, width="75dp", background_normal='', background_color=[1, 0.43, 0, 1], color=[1, 1, 1, 1], bold=True, on_release=self.send_message)
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(send_btn)
        self.layout.add_widget(input_layout)
        
        # 3. Message Stream
        scroll = ScrollView()
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=12)
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        scroll.add_widget(self.chat_list)
        self.layout.add_widget(scroll)
        
        self.add_widget(self.layout)
        
        # 🚀 HARDWARE SOFT KEYBOARD LISTENER ATTACHED HERE
        Window.bind(on_keyboard_height=self.force_layout_above_keyboard)

    def force_layout_above_keyboard(self, window, height):
        if height > 0: self.layout.padding = [0, 0, 0, height]
        else: self.layout.padding = [0, 0, 0, 0]

    def _update_rect(self, instance, value): self.rect.pos = instance.pos; self.rect.size = instance.size
    def _update_header_rect(self, instance, value): self.header_rect.pos = instance.pos; self.header_rect.size = instance.size

    def setup_chat_room(self, chat_id, is_group=False):
        self.username = store.get('profile')['username']
        self.chat_id = chat_id
        
        if is_group:
            self.title_label.text = chat_id.replace("GP_", "👥 Group: ")
        else:
            recipient = chat_id.replace(self.username, "").replace("_AND_", "")
            self.title_label.text = f"👤 Chat: {recipient}"
            
        self.chat_list.clear_widgets()
        self.last_fetched_keys.clear()
        Clock.schedule_interval(self.fetch_messages, 0.5)

    def send_message(self, instance):
        msg_text = self.msg_input.text.strip()
        if msg_text and self.chat_id:
            payload = json.dumps({"sender": self.username, "message": msg_text})
            self.msg_input.text = ""
            UrlRequest(f"{FIREBASE_URL}chats/{self.chat_id}/messages.json", req_body=payload, method='POST', on_success=lambda req, res: self.fetch_messages(0))

    def fetch_messages(self, dt):
        if not self.chat_id: return False
        UrlRequest(f"{FIREBASE_URL}chats/{self.chat_id}/messages.json", on_success=self.parse_messages)

    def parse_messages(self, req, result):
        if result and self.chat_id:
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
                        card_color = [1, 0.43, 0, 0.95]
                    else:
                        row_box.padding = [5, 2, 50, 2]
                        row_box.pos_hint = {"left": 1.0}
                        card_color = [0.16, 0.16, 0.16, 1]

                    with bubble_card.canvas.before:
                        Color(*card_color)
                        bubble_card.bg_shape = RoundedRectangle(size=bubble_card.size, pos=bubble_card.pos, radius=[10])
                    bubble_card.bind(pos=lambda inst, v: setattr(inst, 'bg_shape.pos', v), size=lambda inst, v: setattr(inst, 'bg_shape.size', v))
                    
                    row_box.add_widget(bubble_card)
                    self.chat_list.add_widget(row_box, index=len(self.chat_list.children))
                    self.last_fetched_keys.add(key)

    def leave_chat(self):
        Clock.unschedule(self.fetch_messages)
        self.chat_id = ""
        self.manager.current = 'hub'


class OrangeChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ChatHubScreen(name='hub'))
        sm.add_widget(ExploreSocialScreen(name='explore'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == "__main__":
    OrangeChatApp().run()
