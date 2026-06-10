import json
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout

Window.softinput_mode = 'resize'

FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"
store = JsonStore('orange_chat_local_v8.json')

# ── Design Tokens ──────────────────────────────────────────────
BG_DEEP        = (0.047, 0.047, 0.047, 1)       # #0C0C0C  – deepest bg
BG_SURFACE     = (0.094, 0.094, 0.094, 1)       # #181818  – cards / panels
BG_ELEVATED    = (0.118, 0.118, 0.118, 1)       # #1E1E1E  – elevated surfaces
BG_INPUT       = (0.141, 0.141, 0.141, 1)       # #242424  – input fields
DIVIDER        = (0.18,  0.18,  0.18,  1)       # subtle separator

ACCENT         = (1.0,   0.431, 0.0,   1)       # #FF6E00  – orange brand
ACCENT_DIM     = (1.0,   0.431, 0.0,   0.15)    # tinted overlay
ACCENT_BUBBLE  = (1.0,   0.431, 0.0,   0.95)    # sent message bubble

TEXT_PRIMARY   = (1.0,   1.0,   1.0,   1)       # pure white
TEXT_SECONDARY = (0.6,   0.6,   0.6,   1)       # muted labels
TEXT_TERTIARY  = (0.38,  0.38,  0.38,  1)       # timestamps / captions

RECV_BUBBLE    = (0.149, 0.149, 0.149, 1)       # #262626 received bubble
RADIUS_LG      = [20]
RADIUS_MD      = [14]
RADIUS_SM      = [10]
# ───────────────────────────────────────────────────────────────


def make_separator(height=1):
    sep = Widget(size_hint_y=None, height=dp(height))
    with sep.canvas:
        Color(*DIVIDER)
        sep.line_rect = Rectangle(size=sep.size, pos=sep.pos)
    sep.bind(size=lambda i, v: setattr(i.line_rect, 'size', v),
             pos=lambda i, v: setattr(i.line_rect, 'pos', v))
    return sep


def paint_bg(widget, color, radius=None):
    with widget.canvas.before:
        Color(*color)
        if radius:
            widget._bg = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        else:
            widget._bg = Rectangle(size=widget.size, pos=widget.pos)
    def _sync(inst, val):
        inst._bg.size = inst.size
        inst._bg.pos  = inst.pos
    widget.bind(size=_sync, pos=_sync)


class IconLabel(Label):
    """Small utility – emoji + text in one widget."""
    pass


# ══════════════════════════════════════════════════════════════
#  WELCOME / REGISTER SCREEN
# ══════════════════════════════════════════════════════════════
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_DEEP)

        root = FloatLayout()

        # ── Glow circle behind logo ──
        glow = Widget(size_hint=(None, None), size=(dp(220), dp(220)),
                      pos_hint={"center_x": 0.5, "center_y": 0.72})
        with glow.canvas:
            Color(1.0, 0.431, 0.0, 0.07)
            glow._circle = Ellipse(size=glow.size, pos=glow.pos)
        glow.bind(size=lambda i,v: setattr(i._circle,'size',v),
                  pos=lambda i,v: setattr(i._circle,'pos',v))
        root.add_widget(glow)

        # ── Logo block ──
        logo_box = BoxLayout(orientation='vertical', spacing=dp(6),
                             size_hint=(None, None), size=(dp(260), dp(90)),
                             pos_hint={"center_x": 0.5, "center_y": 0.72})
        logo_icon = Label(text="🟠", font_size=sp(44),
                          size_hint_y=None, height=dp(52))
        logo_text = Label(text="OrangeChat",
                          font_size=sp(26), bold=True,
                          color=ACCENT, size_hint_y=None, height=dp(36))
        logo_box.add_widget(logo_icon)
        logo_box.add_widget(logo_text)
        root.add_widget(logo_box)

        tagline = Label(text="Connect. Message. Belong.",
                        font_size=sp(13), color=TEXT_TERTIARY,
                        size_hint=(None, None), size=(dp(280), dp(22)),
                        pos_hint={"center_x": 0.5, "center_y": 0.62})
        root.add_widget(tagline)

        # ── Card ──
        card = BoxLayout(orientation='vertical', spacing=dp(14),
                         padding=[dp(24), dp(28), dp(24), dp(28)],
                         size_hint=(0.9, None), height=dp(290),
                         pos_hint={"center_x": 0.5, "center_y": 0.33})
        paint_bg(card, BG_SURFACE, RADIUS_LG)

        section_lbl = Label(text="Create your account",
                            font_size=sp(15), bold=True, color=TEXT_PRIMARY,
                            size_hint_y=None, height=dp(22), halign="left")
        section_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        card.add_widget(section_lbl)

        sub_lbl = Label(text="Choose a unique username to get started",
                        font_size=sp(12), color=TEXT_SECONDARY,
                        size_hint_y=None, height=dp(18), halign="left")
        sub_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        card.add_widget(sub_lbl)

        card.add_widget(Widget(size_hint_y=None, height=dp(4)))

        self.username_input = TextInput(
            hint_text="Username  (e.g. ALEX_99)",
            multiline=False,
            padding=[dp(16), dp(14), dp(16), dp(14)],
            background_normal='', background_color=BG_INPUT,
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            cursor_color=ACCENT,
            font_size=sp(14),
            size_hint_y=None, height=dp(50))
        card.add_widget(self.username_input)

        self.bio_input = TextInput(
            hint_text="Bio  (optional)",
            multiline=False,
            padding=[dp(16), dp(14), dp(16), dp(14)],
            background_normal='', background_color=BG_INPUT,
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            cursor_color=ACCENT,
            font_size=sp(14),
            size_hint_y=None, height=dp(50))
        card.add_widget(self.bio_input)

        card.add_widget(Widget(size_hint_y=None, height=dp(4)))

        btn = Button(
            text="Get Started →",
            background_normal='', background_color=ACCENT,
            color=TEXT_PRIMARY, bold=True,
            font_size=sp(15),
            size_hint_y=None, height=dp(52),
            on_release=self.register_profile)
        paint_bg(btn, ACCENT, RADIUS_MD)
        card.add_widget(btn)

        root.add_widget(card)

        footer = Label(
            text="© 2026 Anuj Sharma",
            font_size=sp(10), color=TEXT_TERTIARY,
            size_hint=(None, None), size=(dp(200), dp(20)),
            pos_hint={"center_x": 0.5, "y": 0.015})
        root.add_widget(footer)

        self.add_widget(root)

    def on_enter(self):
        if store.exists('profile'):
            self.manager.current = 'hub'

    def register_profile(self, instance):
        username = self.username_input.text.strip().upper().replace(" ", "_")
        bio      = self.bio_input.text.strip()
        if not username:
            return
        payload = json.dumps({"username": username, "bio": bio})
        UrlRequest(f"{FIREBASE_URL}users/{username}.json",
                   req_body=payload, method='PUT',
                   on_success=lambda r, res: self._save(username, bio))

    def _save(self, username, bio):
        store.put('profile', username=username, bio=bio)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'hub'


# ══════════════════════════════════════════════════════════════
#  CHAT HUB SCREEN
# ══════════════════════════════════════════════════════════════
class ChatHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_DEEP)

        self.my_id   = ""
        self._mode   = "dm"

        root = BoxLayout(orientation='vertical')

        # ── Top Header ──
        header = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=dp(64),
                           padding=[dp(18), dp(10), dp(14), dp(10)])
        paint_bg(header, BG_SURFACE)

        self.avatar_lbl = Label(text="🟠", font_size=sp(22),
                                size_hint=(None, 1), width=dp(36))
        self.profile_lbl = Label(text="OrangeChat",
                                 font_size=sp(17), bold=True,
                                 color=TEXT_PRIMARY, halign="left")
        self.profile_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))

        explore_btn = Button(
            text="Explore",
            size_hint=(None, None), size=(dp(82), dp(36)),
            pos_hint={"center_y": 0.5},
            background_normal='', background_color=(0,0,0,0),
            color=ACCENT, bold=True, font_size=sp(13),
            on_release=lambda x: self._go_explore())
        paint_bg(explore_btn, ACCENT_DIM, RADIUS_SM)

        header.add_widget(self.avatar_lbl)
        header.add_widget(self.profile_lbl)
        header.add_widget(explore_btn)
        root.add_widget(header)
        root.add_widget(make_separator())

        # ── Tab bar ──
        tab_bar = BoxLayout(orientation='horizontal',
                            size_hint_y=None, height=dp(46),
                            padding=[dp(16), dp(6), dp(16), dp(0)])
        paint_bg(tab_bar, BG_SURFACE)

        self.dm_tab = self._make_tab("Messages", active=True,
                                     on_release=lambda x: self._switch_tab("dm"))
        self.gp_tab = self._make_tab("Groups", active=False,
                                     on_release=lambda x: self._switch_tab("group"))

        tab_bar.add_widget(self.dm_tab)
        tab_bar.add_widget(Widget())
        tab_bar.add_widget(self.gp_tab)
        root.add_widget(tab_bar)
        root.add_widget(make_separator())

        # ── New-group row (hidden by default, shown in group tab) ──
        self.gp_creation_row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(0),
            padding=[dp(14), dp(0), dp(14), dp(0)], spacing=dp(10),
            opacity=0)
        paint_bg(self.gp_creation_row, BG_ELEVATED)
        self.gp_name_in = TextInput(
            hint_text="New group name…",
            multiline=False,
            background_normal='', background_color=BG_INPUT,
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            cursor_color=ACCENT,
            font_size=sp(14),
            padding=[dp(12), dp(10)])
        make_gp_btn = Button(
            text="Create",
            size_hint=(None, None), size=(dp(74), dp(40)),
            pos_hint={"center_y": 0.5},
            background_normal='', background_color=ACCENT,
            color=TEXT_PRIMARY, bold=True, font_size=sp(13),
            on_release=self._fire_group_creation)
        paint_bg(make_gp_btn, ACCENT, RADIUS_SM)
        self.gp_creation_row.add_widget(self.gp_name_in)
        self.gp_creation_row.add_widget(make_gp_btn)
        root.add_widget(self.gp_creation_row)

        # ── Scroll feed ──
        scroll = ScrollView(do_scroll_x=False)
        self.feed_layout = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(1), padding=[0, dp(6), 0, dp(6)])
        self.feed_layout.bind(minimum_height=self.feed_layout.setter('height'))
        scroll.add_widget(self.feed_layout)
        root.add_widget(scroll)

        self.add_widget(root)

    # ── helpers ──

    def _make_tab(self, text, active, on_release):
        btn = Button(
            text=text,
            size_hint=(None, None), size=(dp(110), dp(36)),
            background_normal='', background_color=(0,0,0,0),
            color=ACCENT if active else TEXT_SECONDARY,
            bold=active, font_size=sp(13),
            on_release=on_release)
        return btn

    def _switch_tab(self, mode):
        self._mode = mode
        active_color   = ACCENT
        inactive_color = TEXT_SECONDARY
        if mode == "dm":
            self.dm_tab.color = active_color;  self.dm_tab.bold = True
            self.gp_tab.color = inactive_color; self.gp_tab.bold = False
            self.gp_creation_row.height  = dp(0)
            self.gp_creation_row.opacity = 0
        else:
            self.gp_tab.color = active_color;  self.gp_tab.bold = True
            self.dm_tab.color = inactive_color; self.dm_tab.bold = False
            self.gp_creation_row.height  = dp(58)
            self.gp_creation_row.opacity = 1
        self.load_chats_view(mode)

    def _go_explore(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'explore'

    def on_pre_enter(self):
        if store.exists('profile'):
            self.my_id = store.get('profile')['username']
            self.profile_lbl.text = self.my_id
            self.load_chats_view(self._mode)

    def load_chats_view(self, mode):
        self.feed_layout.clear_widgets()
        UrlRequest(f"{FIREBASE_URL}chats.json",
                   on_success=lambda req, res: self._populate(res, mode))

    def _fire_group_creation(self, *_):
        gp_name = self.gp_name_in.text.strip().upper().replace(" ", "_")
        if gp_name:
            self.gp_name_in.text = ""
            cs = self.manager.get_screen('chat')
            cs.setup_chat_room(f"GP_{gp_name}", is_group=True)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'chat'

    def _populate(self, result, mode):
        if not result:
            self._empty_state()
            return
        count = 0
        for chat_id, data in result.items():
            if mode == "group" and chat_id.startswith("GP_"):
                name = chat_id.replace("GP_", "").replace("_", " ").title()
                self._add_row(chat_id, f"👥  {name}", subtitle="Group chat", is_group=True)
                count += 1
            elif mode == "dm" and not chat_id.startswith("GP_") and self.my_id in chat_id:
                receiver = chat_id.replace(self.my_id, "").replace("_AND_", "")
                self._add_row(chat_id, receiver, subtitle="Tap to open chat", is_group=False)
                count += 1
        if count == 0:
            self._empty_state()

    def _empty_state(self):
        lbl = Label(
            text="No conversations yet.\nTap Explore to find someone!",
            color=TEXT_TERTIARY, font_size=sp(13),
            halign="center", valign="middle",
            size_hint_y=None, height=dp(100))
        lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        self.feed_layout.add_widget(lbl)

    def _add_row(self, target_id, label_text, subtitle, is_group):
        row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(70),
            padding=[dp(16), dp(10), dp(12), dp(10)], spacing=dp(14))
        paint_bg(row, BG_DEEP)

        # Avatar circle
        av = Label(
            text=("👥" if is_group else label_text[0].upper()),
            font_size=sp(18),
            size_hint=(None, None), size=(dp(46), dp(46)))
        paint_bg(av, BG_ELEVATED, [dp(23)])
        av.bold = True

        # Text block
        txt_col = BoxLayout(orientation='vertical', spacing=dp(3))
        name_lbl = Label(
            text=label_text, bold=True, font_size=sp(14),
            color=TEXT_PRIMARY, halign="left", valign="middle",
            size_hint_y=None, height=dp(20))
        name_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        sub_lbl = Label(
            text=subtitle, font_size=sp(11),
            color=TEXT_TERTIARY, halign="left", valign="middle",
            size_hint_y=None, height=dp(16))
        sub_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        txt_col.add_widget(name_lbl)
        txt_col.add_widget(sub_lbl)

        chevron = Label(text="›", font_size=sp(22), color=TEXT_TERTIARY,
                        size_hint=(None, 1), width=dp(20))

        row.add_widget(av)
        row.add_widget(txt_col)
        row.add_widget(chevron)

        # Make whole row tappable
        btn = Button(
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
            background_normal='', background_color=(0,0,0,0),
            on_release=lambda x: self._open(target_id, is_group))
        fl = FloatLayout(size_hint_y=None, height=dp(70))
        fl.add_widget(row)
        fl.add_widget(btn)
        self.feed_layout.add_widget(fl)
        self.feed_layout.add_widget(make_separator())

    def _open(self, chat_id, is_group):
        cs = self.manager.get_screen('chat')
        cs.setup_chat_room(chat_id, is_group=is_group)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'chat'


# ══════════════════════════════════════════════════════════════
#  EXPLORE SCREEN
# ══════════════════════════════════════════════════════════════
class ExploreSocialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_DEEP)

        root = BoxLayout(orientation='vertical')

        # Header
        header = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=dp(64),
                           padding=[dp(6), dp(12), dp(16), dp(12)])
        paint_bg(header, BG_SURFACE)

        back_btn = Button(
            text="‹", font_size=sp(26),
            size_hint=(None, 1), width=dp(44),
            background_normal='', background_color=(0,0,0,0),
            color=ACCENT, bold=True,
            on_release=self._go_back)
        hdr_title = Label(text="Find People",
                          font_size=sp(17), bold=True, color=TEXT_PRIMARY)
        header.add_widget(back_btn)
        header.add_widget(hdr_title)
        root.add_widget(header)
        root.add_widget(make_separator())

        # Search bar
        search_row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(64),
            padding=[dp(14), dp(10), dp(14), dp(10)], spacing=dp(10))
        paint_bg(search_row, BG_SURFACE)

        self.search_input = TextInput(
            hint_text="Search by username…",
            multiline=False,
            background_normal='', background_color=BG_INPUT,
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            cursor_color=ACCENT,
            font_size=sp(14),
            padding=[dp(14), dp(12)])
        search_btn = Button(
            text="Search",
            size_hint=(None, 1), width=dp(80),
            background_normal='', background_color=ACCENT,
            color=TEXT_PRIMARY, bold=True, font_size=sp(13),
            on_release=self._search)
        paint_bg(search_btn, ACCENT, RADIUS_SM)
        search_row.add_widget(self.search_input)
        search_row.add_widget(search_btn)
        root.add_widget(search_row)
        root.add_widget(make_separator())

        scroll = ScrollView(do_scroll_x=False)
        self.results_layout = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(1), padding=[0, dp(8), 0, dp(8)])
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll.add_widget(self.results_layout)
        root.add_widget(scroll)

        self.add_widget(root)

    def _go_back(self, *_):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'hub'

    def _search(self, *_):
        self.results_layout.clear_widgets()
        query = self.search_input.text.strip().upper()
        if query:
            UrlRequest(f"{FIREBASE_URL}users/{query}.json",
                       on_success=self._show_result)

    def _show_result(self, req, res):
        if not res:
            lbl = Label(text="No user found with that username.",
                        color=TEXT_TERTIARY, font_size=sp(13),
                        size_hint_y=None, height=dp(60),
                        halign="center")
            lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
            self.results_layout.add_widget(lbl)
            return

        my_id = store.get('profile')['username']
        target = res['username']
        if target == my_id:
            return

        card = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(72),
            padding=[dp(16), dp(10), dp(12), dp(10)], spacing=dp(14))
        paint_bg(card, BG_SURFACE)

        av = Label(text=target[0].upper(), font_size=sp(18), bold=True,
                   size_hint=(None, None), size=(dp(46), dp(46)),
                   color=ACCENT)
        paint_bg(av, ACCENT_DIM, [dp(23)])

        txt_col = BoxLayout(orientation='vertical', spacing=dp(3))
        n = Label(text=target, bold=True, font_size=sp(14),
                  color=TEXT_PRIMARY, halign="left",
                  size_hint_y=None, height=dp(20))
        n.bind(size=lambda i,v: setattr(i,'text_size',v))
        b = Label(text=res.get('bio', 'No bio yet'),
                  font_size=sp(11), color=TEXT_TERTIARY,
                  halign="left", size_hint_y=None, height=dp(16))
        b.bind(size=lambda i,v: setattr(i,'text_size',v))
        txt_col.add_widget(n)
        txt_col.add_widget(b)

        chat_btn = Button(
            text="Message",
            size_hint=(None, None), size=(dp(88), dp(36)),
            pos_hint={"center_y": 0.5},
            background_normal='', background_color=(0,0,0,0),
            color=ACCENT, bold=True, font_size=sp(12),
            on_release=lambda x: self._open_dm(my_id, target))
        paint_bg(chat_btn, ACCENT_DIM, RADIUS_SM)

        card.add_widget(av)
        card.add_widget(txt_col)
        card.add_widget(chat_btn)
        self.results_layout.add_widget(card)

    def _open_dm(self, my_id, target_id):
        dm_id = (f"{my_id}_AND_{target_id}"
                 if my_id < target_id
                 else f"{target_id}_AND_{my_id}")
        payload = json.dumps({"active": True})
        UrlRequest(f"{FIREBASE_URL}chats/{dm_id}/meta.json",
                   req_body=payload, method='PUT',
                   on_success=lambda r, re: self._enter(dm_id))

    def _enter(self, room_id):
        cs = self.manager.get_screen('chat')
        cs.setup_chat_room(room_id, is_group=False)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'chat'


# ══════════════════════════════════════════════════════════════
#  CHAT SCREEN
# ══════════════════════════════════════════════════════════════
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username         = ""
        self.chat_id          = ""
        self.last_fetched_keys = set()

        paint_bg(self, BG_DEEP)
        Window.bind(on_keyboard_height=self._adjust_for_keyboard)

        self._root = BoxLayout(orientation='vertical')

        # ── Header ──
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(64),
            padding=[dp(6), dp(12), dp(16), dp(12)], spacing=dp(8))
        paint_bg(header, BG_SURFACE)

        back_btn = Button(
            text="‹", font_size=sp(26),
            size_hint=(None, 1), width=dp(44),
            background_normal='', background_color=(0,0,0,0),
            color=ACCENT, bold=True,
            on_release=lambda x: self._leave())
        self._peer_av = Label(text="?", font_size=sp(16), bold=True,
                              size_hint=(None, None), size=(dp(40), dp(40)),
                              color=ACCENT)
        paint_bg(self._peer_av, ACCENT_DIM, [dp(20)])

        name_col = BoxLayout(orientation='vertical', spacing=dp(1))
        self.title_label = Label(
            text="Chat", bold=True, font_size=sp(14),
            color=TEXT_PRIMARY, halign="left", size_hint_y=None, height=dp(20))
        self.title_label.bind(size=lambda i,v: setattr(i,'text_size',v))
        self._status_lbl = Label(
            text="online", font_size=sp(11),
            color=(0.3, 0.85, 0.46, 1),          # green dot feel
            halign="left", size_hint_y=None, height=dp(14))
        self._status_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
        name_col.add_widget(self.title_label)
        name_col.add_widget(self._status_lbl)

        header.add_widget(back_btn)
        header.add_widget(self._peer_av)
        header.add_widget(name_col)
        self._root.add_widget(header)
        self._root.add_widget(make_separator())

        # ── Message scroll area ──
        self._scroll = ScrollView(do_scroll_x=False)
        self.chat_list = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=dp(6), padding=[dp(12), dp(10), dp(12), dp(10)])
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        self._scroll.add_widget(self.chat_list)
        self._root.add_widget(self._scroll)

        # ── Input bar ──
        input_bar = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(62),
            padding=[dp(12), dp(10), dp(12), dp(10)], spacing=dp(10))
        paint_bg(input_bar, BG_SURFACE)

        self.msg_input = TextInput(
            hint_text="Type a message…",
            multiline=False,
            background_normal='', background_color=BG_INPUT,
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_TERTIARY,
            cursor_color=ACCENT,
            font_size=sp(14),
            padding=[dp(14), dp(10)])
        send_btn = Button(
            text="➤",
            font_size=sp(20),
            size_hint=(None, None), size=(dp(44), dp(44)),
            pos_hint={"center_y": 0.5},
            background_normal='', background_color=ACCENT,
            color=TEXT_PRIMARY, bold=True,
            on_release=self._send)
        paint_bg(send_btn, ACCENT, [dp(22)])
        input_bar.add_widget(self.msg_input)
        input_bar.add_widget(send_btn)

        self._root.add_widget(make_separator())
        self._root.add_widget(input_bar)

        self.add_widget(self._root)

    def _adjust_for_keyboard(self, window, height):
        self._root.padding = [0, 0, 0, height] if height > 0 else [0, 0, 0, 0]

    def setup_chat_room(self, chat_id, is_group=False):
        self.username = store.get('profile')['username']
        self.chat_id  = chat_id
        self.last_fetched_keys.clear()
        self.chat_list.clear_widgets()

        if is_group:
            name = chat_id.replace("GP_", "").replace("_", " ").title()
            self.title_label.text  = name
            self._peer_av.text     = "👥"
            self._status_lbl.text  = "group"
        else:
            recipient = chat_id.replace(self.username, "").replace("_AND_", "")
            self.title_label.text  = recipient
            self._peer_av.text     = recipient[0].upper() if recipient else "?"
            self._status_lbl.text  = "online"

        Clock.schedule_interval(self._poll, 0.8)

    def _send(self, *_):
        text = self.msg_input.text.strip()
        if text and self.chat_id:
            payload = json.dumps({"sender": self.username, "message": text})
            self.msg_input.text = ""
            UrlRequest(f"{FIREBASE_URL}chats/{self.chat_id}/messages.json",
                       req_body=payload, method='POST',
                       on_success=lambda r, res: self._poll(0))

    def _poll(self, dt):
        if not self.chat_id:
            return False
        UrlRequest(f"{FIREBASE_URL}chats/{self.chat_id}/messages.json",
                   on_success=self._render_messages)

    def _render_messages(self, req, result):
        if not result or not self.chat_id:
            return
        for key, val in result.items():
            if key in self.last_fetched_keys:
                continue
            self.last_fetched_keys.add(key)

            is_me = val['sender'].strip().upper() == self.username.strip().upper()
            self._add_bubble(val['sender'], val['message'], is_me)

        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self._scroll, 'scroll_y', 0), 0.05)

    def _add_bubble(self, sender, message, is_me):
        # Outer row aligns bubble left or right
        row = BoxLayout(orientation='horizontal',
                        size_hint_y=None, padding=[0, dp(2), 0, dp(2)])

        # Inner bubble
        bubble = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(3))

        # Sender name (only in group / received)
        if not is_me:
            sender_lbl = Label(
                text=sender, font_size=sp(11), bold=True,
                color=ACCENT,
                size_hint_y=None, height=dp(16),
                halign="left")
            sender_lbl.bind(size=lambda i,v: setattr(i,'text_size',v))
            bubble.add_widget(sender_lbl)

        msg_lbl = Label(
            text=message,
            font_size=sp(14),
            color=TEXT_PRIMARY if is_me else TEXT_PRIMARY,
            halign="left", valign="top",
            text_size=(dp(220), None))
        msg_lbl.bind(texture_size=lambda i,v: setattr(i,'size',v))

        bubble.add_widget(msg_lbl)

        # Size bubble to content
        def _size_bubble(inst, val):
            w = val[0] + dp(24)
            h = val[1] + dp(18) + (dp(18) if not is_me else 0)
            bubble.size = (w, h)
        msg_lbl.bind(texture_size=_size_bubble)

        # Colours & radius
        if is_me:
            color  = ACCENT_BUBBLE
            radius = [dp(16), dp(4), dp(16), dp(16)]
        else:
            color  = RECV_BUBBLE
            radius = [dp(4), dp(16), dp(16), dp(16)]

        paint_bg(bubble, color, radius)

        # Filler widgets for alignment
        spacer = Widget()
        if is_me:
            row.add_widget(spacer)
            row.add_widget(bubble)
            row.padding = [dp(60), 0, dp(8), 0]
        else:
            row.add_widget(bubble)
            row.add_widget(spacer)
            row.padding = [dp(8), 0, dp(60), 0]

        # Row height tracks bubble
        def _row_h(inst, val):
            row.height = val[1] + dp(4)
        bubble.bind(size=_row_h)

        self.chat_list.add_widget(row)

    def _leave(self):
        Clock.unschedule(self._poll)
        self.chat_id = ""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'hub'


# ══════════════════════════════════════════════════════════════
#  APP
# ══════════════════════════════════════════════════════════════
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
