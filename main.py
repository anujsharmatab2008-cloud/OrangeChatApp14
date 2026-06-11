import os
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
from kivy.uix.widget import Widget
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line, Mesh
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp, sp

Window.softinput_mode = 'resize'

FIREBASE_URL = "https://orangechat-bf085-default-rtdb.firebaseio.com/"
store = JsonStore('orange_chat_local_v9.json')


# ════════════════════════════════════════════════════════════════
#  COLOUR TOKENS  – WhatsApp dark theme
# ════════════════════════════════════════════════════════════════
def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)


BG_APP        = hx("0B141A")   # main background
BG_HEADER     = hx("1F2C34")   # app bar / bottom bar
BG_PANEL      = hx("182229")   # rows / cards
BG_INPUT      = hx("2A3942")   # text inputs
DIVIDER       = hx("222D34")
ACCENT        = hx("00A884")   # whatsapp teal-green
ACCENT_DIM    = (0.0, 0.659, 0.518, 0.16)
BUBBLE_SENT   = hx("005C4B")
BUBBLE_RECV   = hx("202C33")
TEXT_PRIMARY  = hx("E9EDEF")
TEXT_SECOND   = hx("8696A0")
TEXT_FAINT    = hx("5B6B73")
ONLINE        = hx("00D9A6")
RADIUS_LG     = [dp(18)]
RADIUS_MD     = [dp(12)]
RADIUS_SM     = [dp(8)]


def paint_bg(widget, color, radius=None):
    with widget.canvas.before:
        Color(*color)
        if radius:
            widget._bg = RoundedRectangle(size=widget.size, pos=widget.pos, radius=radius)
        else:
            widget._bg = Rectangle(size=widget.size, pos=widget.pos)

    def _sync(inst, val):
        inst._bg.size = inst.size
        inst._bg.pos = inst.pos
    widget.bind(size=_sync, pos=_sync)


def make_separator():
    sep = Widget(size_hint_y=None, height=dp(1))
    paint_bg(sep, DIVIDER)
    return sep


# ════════════════════════════════════════════════════════════════
#  VECTOR ICONS  (replace tofu-box emoji with hand-drawn glyphs)
# ════════════════════════════════════════════════════════════════
class Icon(Widget):
    """Tiny vector icon drawn with Line/Ellipse/Mesh – no font dependency."""

    def __init__(self, name, color=TEXT_PRIMARY, line_w=1.8, mirror=False, **kwargs):
        super().__init__(**kwargs)
        self.icon_name = name
        self.icon_color = color
        self.line_w = line_w
        self.mirror = mirror
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *a):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        s = min(w, h)
        ox, oy = x + (w - s) / 2, y + (h - s) / 2  # origin of centred square
        lw = dp(self.line_w)

        def m(px):
            """Mirror an x-coordinate horizontally if requested."""
            if self.mirror:
                return ox + (s - (px - ox))
            return px

        with self.canvas:
            Color(*self.icon_color)
            n = self.icon_name

            if n == 'back':
                Line(points=[m(ox + 0.62 * s), oy + 0.20 * s,
                              m(ox + 0.34 * s), oy + 0.50 * s,
                              m(ox + 0.62 * s), oy + 0.80 * s],
                     width=lw, cap='round', joint='round')

            elif n == 'search':
                Line(circle=(ox + 0.42 * s, oy + 0.58 * s, 0.20 * s), width=lw)
                Line(points=[ox + 0.56 * s, oy + 0.44 * s,
                              ox + 0.82 * s, oy + 0.18 * s],
                     width=lw, cap='round')

            elif n == 'more':
                for dy in (0.22, 0.50, 0.78):
                    Ellipse(pos=(ox + 0.46 * s, oy + dy * s - 0.045 * s),
                            size=(0.09 * s, 0.09 * s))

            elif n == 'camera':
                Line(rounded_rectangle=(ox + 0.08 * s, oy + 0.14 * s,
                                         0.84 * s, 0.58 * s, 0.06 * s), width=lw)
                Line(circle=(ox + 0.5 * s, oy + 0.43 * s, 0.17 * s), width=lw)
                Line(points=[ox + 0.34 * s, oy + 0.72 * s,
                              ox + 0.34 * s, oy + 0.80 * s,
                              ox + 0.62 * s, oy + 0.80 * s,
                              ox + 0.62 * s, oy + 0.72 * s],
                     width=lw, joint='round')

            elif n == 'send':
                Mesh(vertices=[
                    ox + 0.16 * s, oy + 0.84 * s, 0, 0,
                    ox + 0.86 * s, oy + 0.50 * s, 0, 0,
                    ox + 0.16 * s, oy + 0.16 * s, 0, 0,
                    ox + 0.38 * s, oy + 0.50 * s, 0, 0,
                ], indices=[0, 1, 2, 3], mode='triangle_fan')

            elif n == 'group':
                Line(circle=(ox + 0.36 * s, oy + 0.52 * s, 0.21 * s), width=lw)
                Line(circle=(ox + 0.64 * s, oy + 0.52 * s, 0.21 * s), width=lw)

            elif n == 'person':
                Ellipse(pos=(ox + 0.32 * s, oy + 0.50 * s), size=(0.36 * s, 0.36 * s))
                Line(rounded_rectangle=(ox + 0.16 * s, oy + 0.04 * s,
                                         0.68 * s, 0.42 * s, 0.20 * s), width=lw)

            elif n == 'check':
                Line(points=[ox + 0.18 * s, oy + 0.50 * s,
                              ox + 0.40 * s, oy + 0.28 * s,
                              ox + 0.84 * s, oy + 0.74 * s],
                     width=lw, cap='round', joint='round')

            elif n == 'double_check':
                for off in (0.0, 0.20):
                    Line(points=[ox + (0.04 + off) * s, oy + 0.50 * s,
                                  ox + (0.26 + off) * s, oy + 0.28 * s,
                                  ox + (0.70 + off) * s, oy + 0.74 * s],
                         width=lw, cap='round', joint='round')

            elif n == 'edit':
                Line(points=[ox + 0.18 * s, oy + 0.18 * s,
                              ox + 0.66 * s, oy + 0.66 * s],
                     width=lw * 1.6, cap='round')
                Line(points=[ox + 0.62 * s, oy + 0.62 * s,
                              ox + 0.84 * s, oy + 0.84 * s],
                     width=lw * 1.6, cap='round')
                Line(points=[ox + 0.16 * s, oy + 0.10 * s,
                              ox + 0.24 * s, oy + 0.18 * s,
                              ox + 0.16 * s, oy + 0.20 * s],
                     width=lw, joint='round', close=True)

            elif n == 'plus':
                Line(points=[ox + 0.5 * s, oy + 0.18 * s, ox + 0.5 * s, oy + 0.82 * s],
                     width=lw * 1.4, cap='round')
                Line(points=[ox + 0.18 * s, oy + 0.5 * s, ox + 0.82 * s, oy + 0.5 * s],
                     width=lw * 1.4, cap='round')

            elif n == 'close':
                Line(points=[ox + 0.22 * s, oy + 0.22 * s, ox + 0.78 * s, oy + 0.78 * s],
                     width=lw, cap='round')
                Line(points=[ox + 0.78 * s, oy + 0.22 * s, ox + 0.22 * s, oy + 0.78 * s],
                     width=lw, cap='round')

            elif n == 'logout':
                Line(rounded_rectangle=(ox + 0.18 * s, oy + 0.16 * s,
                                         0.40 * s, 0.68 * s, 0.05 * s), width=lw)
                Line(points=[ox + 0.40 * s, oy + 0.50 * s, ox + 0.86 * s, oy + 0.50 * s],
                     width=lw, cap='round')
                Line(points=[ox + 0.68 * s, oy + 0.34 * s,
                              ox + 0.86 * s, oy + 0.50 * s,
                              ox + 0.68 * s, oy + 0.66 * s],
                     width=lw, cap='round', joint='round')


def icon_btn(name, on_release, size=dp(40), color=TEXT_PRIMARY, icon_pad=0.55, mirror=False):
    """A transparent square button containing a vector icon."""
    btn = Button(size_hint=(None, None), size=(size, size),
                  background_normal='', background_color=(0, 0, 0, 0),
                  on_release=on_release)
    ic = Icon(name, color=color, mirror=mirror,
              size_hint=(None, None), size=(size * icon_pad, size * icon_pad),
              pos_hint={'center_x': 0.5, 'center_y': 0.5})
    btn.add_widget(ic)
    return btn


# ════════════════════════════════════════════════════════════════
#  CIRCLE AVATAR  (shows uploaded photo OR initial letter)
# ════════════════════════════════════════════════════════════════
class CircleAvatar(Widget):
    def __init__(self, text="?", source=None, bg_color=BG_INPUT,
                 text_color=ACCENT, font_size=sp(16), **kwargs):
        super().__init__(**kwargs)
        self._bg_color = bg_color
        self._text_color = text_color
        self._font_size = font_size
        self._has_image = False

        with self.canvas:
            self._color_inst = Color(*bg_color)
            self._ellipse = Ellipse(pos=self.pos, size=self.size)

        self._label = Label(text=text, color=text_color, bold=True,
                             font_size=font_size)
        self.add_widget(self._label)

        self.bind(pos=self._sync, size=self._sync)
        if source and os.path.exists(source):
            self.set_image(source)

    def _sync(self, *a):
        self._ellipse.pos = self.pos
        self._ellipse.size = self.size
        self._label.pos = self.pos
        self._label.size = self.size

    def set_image(self, path):
        try:
            tex = CoreImage(path).texture
            tex.flip_vertical()
            tex.wrap = 'clamp_to_edge'
            self._ellipse.texture = tex
            self._color_inst.rgba = (1, 1, 1, 1)
            self._label.text = ""
            self._has_image = True
        except Exception:
            pass

    def set_letter(self, letter):
        self._ellipse.texture = None
        self._color_inst.rgba = self._bg_color
        self._label.text = letter
        self._has_image = False


# ════════════════════════════════════════════════════════════════
#  PROFILE-PICTURE PICKER  (plyer file chooser, gallery on phone)
# ════════════════════════════════════════════════════════════════
def request_storage_permissions():
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.READ_MEDIA_IMAGES,
        ])
    except Exception:
        pass


def pick_image(callback):
    """Open the native gallery / file picker. callback(path_or_None)."""
    try:
        from plyer import filechooser

        def _on_sel(selection):
            path = selection[0] if selection else None
            Clock.schedule_once(lambda dt: callback(path))

        filechooser.open_file(on_selection=_on_sel,
                               filters=[("Images", "*.png", "*.jpg", "*.jpeg")])
    except Exception:
        callback(None)


# ════════════════════════════════════════════════════════════════
#  WELCOME / REGISTER SCREEN
# ════════════════════════════════════════════════════════════════
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_APP)
        self.picked_avatar = None

        root = FloatLayout()

        logo_box = BoxLayout(orientation='vertical', spacing=dp(4),
                              size_hint=(None, None), size=(dp(260), dp(70)),
                              pos_hint={'center_x': 0.5, 'center_y': 0.86})
        title = Label(text="OrangeChat", font_size=sp(26), bold=True,
                       color=ACCENT, size_hint_y=None, height=dp(36))
        sub = Label(text="Simple. Secure. Reliable messaging.",
                     font_size=sp(12), color=TEXT_SECOND,
                     size_hint_y=None, height=dp(20))
        logo_box.add_widget(title)
        logo_box.add_widget(sub)
        root.add_widget(logo_box)

        # ── Avatar picker ──
        avatar_wrap = FloatLayout(size_hint=(None, None), size=(dp(110), dp(110)),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.62})
        self.avatar = CircleAvatar(text="", source=None,
                                    bg_color=BG_PANEL, text_color=ACCENT,
                                    size_hint=(1, 1))
        self._person_icon = Icon('person', color=TEXT_FAINT,
                                  size_hint=(None, None), size=(dp(60), dp(60)),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.5})
        avatar_wrap.add_widget(self.avatar)
        avatar_wrap.add_widget(self._person_icon)

        cam_btn = Button(size_hint=(None, None), size=(dp(34), dp(34)),
                          pos_hint={'right': 1, 'y': 0},
                          background_normal='', background_color=(0, 0, 0, 0),
                          on_release=self._choose_avatar)
        paint_bg(cam_btn, ACCENT, [dp(17)])
        cam_icon = Icon('camera', color=BG_APP,
                        size_hint=(None, None), size=(dp(20), dp(20)),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5})
        cam_btn.add_widget(cam_icon)
        avatar_wrap.add_widget(cam_btn)
        root.add_widget(avatar_wrap)

        # ── Card ──
        card = BoxLayout(orientation='vertical', spacing=dp(14),
                          padding=[dp(24), dp(26), dp(24), dp(26)],
                          size_hint=(0.9, None), height=dp(230),
                          pos_hint={'center_x': 0.5, 'center_y': 0.32})
        paint_bg(card, BG_PANEL, RADIUS_LG)

        section_lbl = Label(text="Create your account", font_size=sp(15),
                             bold=True, color=TEXT_PRIMARY,
                             size_hint_y=None, height=dp(22), halign="left")
        section_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        card.add_widget(section_lbl)

        self.username_input = TextInput(
            hint_text="Username (e.g. ALEX_99)", multiline=False,
            padding=[dp(16), dp(14)], background_normal='',
            background_color=BG_INPUT, foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
            font_size=sp(14), size_hint_y=None, height=dp(50))
        card.add_widget(self.username_input)

        self.bio_input = TextInput(
            hint_text="Bio (optional)", multiline=False,
            padding=[dp(16), dp(14)], background_normal='',
            background_color=BG_INPUT, foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
            font_size=sp(14), size_hint_y=None, height=dp(50))
        card.add_widget(self.bio_input)

        btn = Button(text="Get Started", background_normal='',
                      background_color=(0, 0, 0, 0), color=BG_APP, bold=True,
                      font_size=sp(15), size_hint_y=None, height=dp(52),
                      on_release=self.register_profile)
        paint_bg(btn, ACCENT, RADIUS_MD)
        card.add_widget(btn)

        root.add_widget(card)

        footer = Label(text="© 2026 Anuj Sharma", font_size=sp(10),
                        color=TEXT_FAINT, size_hint=(None, None),
                        size=(dp(200), dp(20)),
                        pos_hint={'center_x': 0.5, 'y': 0.015})
        root.add_widget(footer)

        self.add_widget(root)

    def on_enter(self):
        request_storage_permissions()
        if store.exists('profile'):
            self.manager.current = 'hub'

    def _choose_avatar(self, *_):
        pick_image(self._on_avatar_picked)

    def _on_avatar_picked(self, path):
        if path:
            self.picked_avatar = path
            self.avatar.set_image(path)
            self._person_icon.opacity = 0

    def register_profile(self, instance):
        username = self.username_input.text.strip().upper().replace(" ", "_")
        bio = self.bio_input.text.strip()
        if not username:
            return
        payload = json.dumps({"username": username, "bio": bio})
        UrlRequest(f"{FIREBASE_URL}users/{username}.json",
                   req_body=payload, method='PUT',
                   on_success=lambda r, res: self._save(username, bio))

    def _save(self, username, bio):
        store.put('profile', username=username, bio=bio,
                  avatar=self.picked_avatar or "")
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'hub'


# ════════════════════════════════════════════════════════════════
#  CHAT HUB SCREEN
# ════════════════════════════════════════════════════════════════
class ChatHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_APP)
        self.my_id = ""
        self._mode = "dm"

        root = BoxLayout(orientation='vertical')

        # ── Header ──
        header = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(58), padding=[dp(12), dp(8)], spacing=dp(10))
        paint_bg(header, BG_HEADER)

        self.my_avatar = CircleAvatar(text="?", bg_color=BG_INPUT,
                                       text_color=ACCENT, font_size=sp(15),
                                       size_hint=(None, None), size=(dp(40), dp(40)))
        avatar_btn = Button(size_hint=(None, None), size=(dp(40), dp(40)),
                             background_normal='', background_color=(0, 0, 0, 0),
                             on_release=lambda x: self._go_profile())
        avatar_holder = FloatLayout(size_hint=(None, None), size=(dp(40), dp(40)))
        avatar_holder.add_widget(self.my_avatar)
        avatar_holder.add_widget(avatar_btn)

        title_lbl = Label(text="OrangeChat", font_size=sp(18), bold=True,
                           color=TEXT_PRIMARY, halign="left")
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))

        header.add_widget(avatar_holder)
        header.add_widget(title_lbl)
        header.add_widget(icon_btn('search', lambda x: self._go_explore(),
                                    color=TEXT_PRIMARY))
        root.add_widget(header)
        root.add_widget(make_separator())

        # ── Tabs ──
        tab_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(46))
        paint_bg(tab_row, BG_HEADER)
        self.dm_tab_btn = Button(text="CHATS", bold=True, font_size=sp(13),
                                  color=ACCENT, background_normal='',
                                  background_color=(0, 0, 0, 0),
                                  on_release=lambda x: self._switch_tab("dm"))
        self.gp_tab_btn = Button(text="GROUPS", bold=True, font_size=sp(13),
                                  color=TEXT_SECOND, background_normal='',
                                  background_color=(0, 0, 0, 0),
                                  on_release=lambda x: self._switch_tab("group"))
        tab_row.add_widget(self.dm_tab_btn)
        tab_row.add_widget(self.gp_tab_btn)
        root.add_widget(tab_row)

        # underline indicator
        self._indicator = Widget(size_hint=(None, None), height=dp(3))
        paint_bg(self._indicator, ACCENT, [dp(2)])
        root.add_widget(self._indicator)
        root.add_widget(make_separator())

        Window.bind(on_resize=lambda *a: Clock.schedule_once(self._position_indicator, 0))
        Clock.schedule_once(self._position_indicator, 0)

        # ── New-group creation row ──
        self.gp_creation_row = BoxLayout(orientation='horizontal',
                                          size_hint_y=None, height=dp(0),
                                          padding=[dp(12), dp(8)], spacing=dp(8),
                                          opacity=0)
        paint_bg(self.gp_creation_row, BG_PANEL)
        self.gp_name_in = TextInput(hint_text="New group name…", multiline=False,
                                     background_normal='', background_color=BG_INPUT,
                                     foreground_color=TEXT_PRIMARY,
                                     hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
                                     font_size=sp(14), padding=[dp(12), dp(10)])
        make_gp_btn = Button(text="Create", size_hint=(None, 1), width=dp(76),
                              background_normal='', background_color=(0, 0, 0, 0),
                              color=BG_APP, bold=True, font_size=sp(13),
                              on_release=self._fire_group_creation)
        paint_bg(make_gp_btn, ACCENT, RADIUS_SM)
        self.gp_creation_row.add_widget(self.gp_name_in)
        self.gp_creation_row.add_widget(make_gp_btn)
        root.add_widget(self.gp_creation_row)

        # ── Feed ──
        scroll = ScrollView(do_scroll_x=False)
        self.feed_layout = BoxLayout(orientation='vertical', size_hint_y=None,
                                      spacing=dp(1))
        self.feed_layout.bind(minimum_height=self.feed_layout.setter('height'))
        scroll.add_widget(self.feed_layout)
        root.add_widget(scroll)

        self.add_widget(root)

        # ── Floating Action Button ──
        fab = Button(size_hint=(None, None), size=(dp(56), dp(56)),
                      pos_hint={'right': 0.96, 'y': 0.04},
                      background_normal='', background_color=(0, 0, 0, 0),
                      on_release=lambda x: self._go_explore())
        paint_bg(fab, ACCENT, [dp(28)])
        fab.add_widget(Icon('plus', color=BG_APP, size_hint=(None, None),
                             size=(dp(26), dp(26)),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        self._fab_holder = FloatLayout(size_hint=(1, 1))
        self._fab_holder.add_widget(fab)
        self.add_widget(self._fab_holder)

    # ── helpers ──
    def _position_indicator(self, *a):
        tab_w = self.dm_tab_btn.width or (Window.width / 2)
        self._indicator.width = tab_w
        self._indicator.x = self.dm_tab_btn.x if self._mode == "dm" else self.gp_tab_btn.x
        self._indicator.y = self.dm_tab_btn.y

    def _switch_tab(self, mode):
        self._mode = mode
        if mode == "dm":
            self.dm_tab_btn.color = ACCENT
            self.gp_tab_btn.color = TEXT_SECOND
            self.gp_creation_row.height = dp(0)
            self.gp_creation_row.opacity = 0
        else:
            self.gp_tab_btn.color = ACCENT
            self.dm_tab_btn.color = TEXT_SECOND
            self.gp_creation_row.height = dp(58)
            self.gp_creation_row.opacity = 1
        self._position_indicator()
        self.load_chats_view(mode)

    def _go_explore(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'explore'

    def _go_profile(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'profile'

    def on_pre_enter(self):
        if store.exists('profile'):
            profile = store.get('profile')
            self.my_id = profile['username']
            avatar_path = profile.get('avatar', '')
            if avatar_path and os.path.exists(avatar_path):
                self.my_avatar.set_image(avatar_path)
            else:
                self.my_avatar.set_letter(self.my_id[0].upper())
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
                self._add_row(chat_id, name, "Group · tap to open", True)
                count += 1
            elif mode == "dm" and not chat_id.startswith("GP_") and self.my_id in chat_id:
                receiver = chat_id.replace(self.my_id, "").replace("_AND_", "")
                self._add_row(chat_id, receiver, "Tap to open conversation", False)
                count += 1
        if count == 0:
            self._empty_state()

    def _empty_state(self):
        lbl = Label(text="No conversations yet.\nTap + to start a new chat.",
                     color=TEXT_FAINT, font_size=sp(13),
                     halign="center", valign="middle",
                     size_hint_y=None, height=dp(120))
        lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.feed_layout.add_widget(lbl)

    def _add_row(self, target_id, label_text, subtitle, is_group):
        fl = FloatLayout(size_hint_y=None, height=dp(70))

        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70),
                         padding=[dp(14), dp(10), dp(14), dp(10)], spacing=dp(12))
        paint_bg(row, BG_APP)

        if is_group:
            av_holder = FloatLayout(size_hint=(None, None), size=(dp(46), dp(46)))
            av = CircleAvatar(text="", bg_color=BG_INPUT, text_color=ACCENT,
                               size_hint=(1, 1))
            av_holder.add_widget(av)
            av_holder.add_widget(Icon('group', color=TEXT_SECOND,
                                       size_hint=(None, None), size=(dp(26), dp(26)),
                                       pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        else:
            av_holder = CircleAvatar(text=label_text[0].upper(), bg_color=BG_INPUT,
                                      text_color=ACCENT, font_size=sp(16),
                                      size_hint=(None, None), size=(dp(46), dp(46)))

        txt_col = BoxLayout(orientation='vertical', spacing=dp(3))
        name_lbl = Label(text=label_text, bold=True, font_size=sp(14),
                          color=TEXT_PRIMARY, halign="left", valign="middle",
                          size_hint_y=None, height=dp(20))
        name_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        sub_lbl = Label(text=subtitle, font_size=sp(11), color=TEXT_FAINT,
                         halign="left", valign="middle", size_hint_y=None, height=dp(16))
        sub_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        txt_col.add_widget(name_lbl)
        txt_col.add_widget(sub_lbl)

        chevron_wrap = FloatLayout(size_hint=(None, 1), width=dp(18))
        chevron_icon = Icon('back', color=TEXT_FAINT, mirror=True,
                             size_hint=(None, None), size=(dp(18), dp(18)),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5})
        chevron_wrap.add_widget(chevron_icon)

        row.add_widget(av_holder)
        row.add_widget(txt_col)
        row.add_widget(chevron_wrap)

        btn = Button(size_hint=(1, 1), background_normal='',
                      background_color=(0, 0, 0, 0),
                      on_release=lambda x: self._open(target_id, is_group))

        fl.add_widget(row)
        fl.add_widget(btn)
        self.feed_layout.add_widget(fl)
        self.feed_layout.add_widget(make_separator())

    def _open(self, chat_id, is_group):
        cs = self.manager.get_screen('chat')
        cs.setup_chat_room(chat_id, is_group=is_group)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'chat'


# ════════════════════════════════════════════════════════════════
#  EXPLORE / NEW CHAT SCREEN
# ════════════════════════════════════════════════════════════════
class ExploreSocialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_APP)

        root = BoxLayout(orientation='vertical')

        header = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(58), padding=[dp(6), dp(8), dp(14), dp(8)],
                            spacing=dp(8))
        paint_bg(header, BG_HEADER)
        header.add_widget(icon_btn('back', self._go_back, color=TEXT_PRIMARY))
        title_lbl = Label(text="New Chat", font_size=sp(17), bold=True,
                          color=TEXT_PRIMARY, halign="left")
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        header.add_widget(title_lbl)
        root.add_widget(header)
        root.add_widget(make_separator())

        search_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=dp(60), padding=[dp(12), dp(8)], spacing=dp(8))
        paint_bg(search_row, BG_HEADER)
        self.search_input = TextInput(hint_text="Search by username…", multiline=False,
                                       background_normal='', background_color=BG_INPUT,
                                       foreground_color=TEXT_PRIMARY,
                                       hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
                                       font_size=sp(14), padding=[dp(14), dp(12)])
        search_btn = Button(text="Search", size_hint=(None, 1), width=dp(80),
                             background_normal='', background_color=(0, 0, 0, 0),
                             color=BG_APP, bold=True, font_size=sp(13),
                             on_release=self._search)
        paint_bg(search_btn, ACCENT, RADIUS_SM)
        search_row.add_widget(self.search_input)
        search_row.add_widget(search_btn)
        root.add_widget(search_row)
        root.add_widget(make_separator())

        scroll = ScrollView(do_scroll_x=False)
        self.results_layout = BoxLayout(orientation='vertical', size_hint_y=None,
                                         spacing=dp(1))
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
            UrlRequest(f"{FIREBASE_URL}users/{query}.json", on_success=self._show_result)

    def _show_result(self, req, res):
        if not res:
            lbl = Label(text="No user found with that username.",
                         color=TEXT_FAINT, font_size=sp(13),
                         size_hint_y=None, height=dp(60), halign="center")
            lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
            self.results_layout.add_widget(lbl)
            return

        my_id = store.get('profile')['username']
        target = res['username']
        if target == my_id:
            return

        fl = FloatLayout(size_hint_y=None, height=dp(72))
        card = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(72),
                          padding=[dp(14), dp(10)], spacing=dp(12))
        paint_bg(card, BG_APP)

        av = CircleAvatar(text=target[0].upper(), bg_color=BG_INPUT, text_color=ACCENT,
                           font_size=sp(16), size_hint=(None, None), size=(dp(46), dp(46)))

        txt_col = BoxLayout(orientation='vertical', spacing=dp(3))
        n = Label(text=target, bold=True, font_size=sp(14), color=TEXT_PRIMARY,
                  halign="left", size_hint_y=None, height=dp(20))
        n.bind(size=lambda i, v: setattr(i, 'text_size', v))
        b = Label(text=res.get('bio', 'Hey there! I am using OrangeChat'),
                  font_size=sp(11), color=TEXT_FAINT, halign="left",
                  size_hint_y=None, height=dp(16))
        b.bind(size=lambda i, v: setattr(i, 'text_size', v))
        txt_col.add_widget(n)
        txt_col.add_widget(b)

        card.add_widget(av)
        card.add_widget(txt_col)

        btn = Button(size_hint=(1, 1), background_normal='',
                      background_color=(0, 0, 0, 0),
                      on_release=lambda x: self._open_dm(my_id, target))
        fl.add_widget(card)
        fl.add_widget(btn)
        self.results_layout.add_widget(fl)
        self.results_layout.add_widget(make_separator())

    def _open_dm(self, my_id, target_id):
        dm_id = (f"{my_id}_AND_{target_id}" if my_id < target_id
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


# ════════════════════════════════════════════════════════════════
#  CHAT SCREEN
# ════════════════════════════════════════════════════════════════
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
        self.chat_id = ""
        self.last_fetched_keys = set()

        paint_bg(self, BG_APP)
        Window.bind(on_keyboard_height=self._adjust_for_keyboard)

        self._root = BoxLayout(orientation='vertical')

        # ── Header ──
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(58),
                            padding=[dp(4), dp(8), dp(12), dp(8)], spacing=dp(8))
        paint_bg(header, BG_HEADER)

        header.add_widget(icon_btn('back', lambda x: self._leave(), color=TEXT_PRIMARY))

        self._peer_av = CircleAvatar(text="?", bg_color=BG_INPUT, text_color=ACCENT,
                                      font_size=sp(15), size_hint=(None, None),
                                      size=(dp(40), dp(40)))
        self._peer_av_holder = FloatLayout(size_hint=(None, None), size=(dp(40), dp(40)))
        self._peer_av_holder.add_widget(self._peer_av)
        self._peer_group_icon = Icon('group', color=TEXT_SECOND,
                                      size_hint=(None, None), size=(dp(24), dp(24)),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                      opacity=0)
        self._peer_av_holder.add_widget(self._peer_group_icon)
        header.add_widget(self._peer_av_holder)

        name_col = BoxLayout(orientation='vertical', spacing=dp(1))
        self.title_label = Label(text="Chat", bold=True, font_size=sp(14),
                                  color=TEXT_PRIMARY, halign="left",
                                  size_hint_y=None, height=dp(20))
        self.title_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self._status_lbl = Label(text="online", font_size=sp(11), color=ONLINE,
                                  halign="left", size_hint_y=None, height=dp(14))
        self._status_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        name_col.add_widget(self.title_label)
        name_col.add_widget(self._status_lbl)
        header.add_widget(name_col)

        self._root.add_widget(header)
        self._root.add_widget(make_separator())

        # ── Messages ──
        self._scroll = ScrollView(do_scroll_x=False)
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None,
                                    spacing=dp(6), padding=[dp(10), dp(10)])
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        self._scroll.add_widget(self.chat_list)
        self._root.add_widget(self._scroll)

        # ── Input bar ──
        input_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(64),
                               padding=[dp(10), dp(8)], spacing=dp(8))
        paint_bg(input_bar, BG_HEADER)

        field_wrap = BoxLayout(orientation='horizontal')
        paint_bg(field_wrap, BG_INPUT, [dp(22)])
        self.msg_input = TextInput(hint_text="Type a message", multiline=False,
                                    background_normal='', background_color=(0, 0, 0, 0),
                                    foreground_color=TEXT_PRIMARY,
                                    hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
                                    font_size=sp(14), padding=[dp(16), dp(13)])
        field_wrap.add_widget(self.msg_input)

        send_btn = Button(size_hint=(None, None), size=(dp(46), dp(46)),
                           pos_hint={'center_y': 0.5}, background_normal='',
                           background_color=(0, 0, 0, 0), on_release=self._send)
        paint_bg(send_btn, ACCENT, [dp(23)])
        send_btn.add_widget(Icon('send', color=BG_APP, size_hint=(None, None),
                                  size=(dp(20), dp(20)),
                                  pos_hint={'center_x': 0.46, 'center_y': 0.5}))

        input_bar.add_widget(field_wrap)
        input_bar.add_widget(send_btn)

        self._root.add_widget(make_separator())
        self._root.add_widget(input_bar)

        self.add_widget(self._root)

    def _adjust_for_keyboard(self, window, height):
        self._root.padding = [0, 0, 0, height] if height > 0 else [0, 0, 0, 0]

    def setup_chat_room(self, chat_id, is_group=False):
        self.username = store.get('profile')['username']
        self.chat_id = chat_id
        self.last_fetched_keys.clear()
        self.chat_list.clear_widgets()

        if is_group:
            name = chat_id.replace("GP_", "").replace("_", " ").title()
            self.title_label.text = name
            self._peer_av.set_letter("")
            self._peer_group_icon.opacity = 1
            self._status_lbl.text = "group chat"
        else:
            recipient = chat_id.replace(self.username, "").replace("_AND_", "")
            self.title_label.text = recipient
            self._peer_av.set_letter(recipient[0].upper() if recipient else "?")
            self._peer_group_icon.opacity = 0
            self._status_lbl.text = "online"

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
        added = False
        for key, val in result.items():
            if key in self.last_fetched_keys:
                continue
            self.last_fetched_keys.add(key)
            is_me = val['sender'].strip().upper() == self.username.strip().upper()
            self._add_bubble(val['sender'], val['message'], is_me)
            added = True
        if added:
            Clock.schedule_once(lambda dt: setattr(self._scroll, 'scroll_y', 0), 0.05)

    def _add_bubble(self, sender, message, is_me):
        row = BoxLayout(orientation='horizontal', size_hint_y=None)

        bubble = BoxLayout(orientation='vertical', size_hint=(None, None),
                            padding=[dp(12), dp(8), dp(12), dp(6)], spacing=dp(2))

        if not is_me:
            sender_lbl = Label(text=sender, font_size=sp(11), bold=True, color=ACCENT,
                                size_hint_y=None, height=dp(16), halign="left")
            sender_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
            bubble.add_widget(sender_lbl)

        msg_lbl = Label(text=message, font_size=sp(14), color=TEXT_PRIMARY,
                        halign="left", valign="top",
                        text_size=(dp(220), None))
        bubble.add_widget(msg_lbl)

        # status row (timestamp + read receipt) for sent messages
        meta_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(14),
                              spacing=dp(4))
        meta_row.add_widget(Widget())
        if is_me:
            meta_row.add_widget(Icon('double_check', color=hx("53BDEB"),
                                      size_hint=(None, None), size=(dp(16), dp(12))))
        bubble.add_widget(meta_row)

        def _size_bubble(inst, val):
            extra_h = dp(18) + (dp(16) if not is_me else 0) + dp(14)
            bubble.width = val[0] + dp(24)
            bubble.height = val[1] + extra_h
        msg_lbl.bind(texture_size=_size_bubble)

        if is_me:
            color = BUBBLE_SENT
            radius = [dp(14), dp(2), dp(14), dp(14)]
        else:
            color = BUBBLE_RECV
            radius = [dp(2), dp(14), dp(14), dp(14)]
        paint_bg(bubble, color, radius)

        if is_me:
            row.padding = [dp(60), 0, dp(6), 0]
            row.add_widget(Widget())
            row.add_widget(bubble)
        else:
            row.padding = [dp(6), 0, dp(60), 0]
            row.add_widget(bubble)
            row.add_widget(Widget())

        def _row_h(inst, val):
            row.height = val[1] + dp(2)
        bubble.bind(size=_row_h)

        self.chat_list.add_widget(row)

    def _leave(self):
        Clock.unschedule(self._poll)
        self.chat_id = ""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'hub'


# ════════════════════════════════════════════════════════════════
#  PROFILE SCREEN
# ════════════════════════════════════════════════════════════════
class AnchorWrap(BoxLayout):
    """Helper to centre a fixed-size FloatLayout horizontally."""
    def __init__(self, child, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None,
                          height=dp(130), **kwargs)
        self.add_widget(Widget())
        self.add_widget(child)
        self.add_widget(Widget())


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        paint_bg(self, BG_APP)

        root = BoxLayout(orientation='vertical')

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(58),
                            padding=[dp(6), dp(8), dp(14), dp(8)], spacing=dp(8))
        paint_bg(header, BG_HEADER)
        header.add_widget(icon_btn('back', self._go_back, color=TEXT_PRIMARY))
        title_lbl = Label(text="Profile", font_size=sp(17), bold=True,
                          color=TEXT_PRIMARY, halign="left")
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        header.add_widget(title_lbl)
        root.add_widget(header)
        root.add_widget(make_separator())

        body = BoxLayout(orientation='vertical', spacing=dp(20),
                          padding=[dp(20), dp(30), dp(20), dp(20)])

        # ── Avatar ──
        avatar_wrap = FloatLayout(size_hint=(None, None), size=(dp(130), dp(130)))
        self.avatar = CircleAvatar(text="?", bg_color=BG_PANEL, text_color=ACCENT,
                                    font_size=sp(36), size_hint=(1, 1))
        avatar_wrap.add_widget(self.avatar)

        cam_btn = Button(size_hint=(None, None), size=(dp(40), dp(40)),
                          pos_hint={'center_x': 0.82, 'center_y': 0.12},
                          background_normal='', background_color=(0, 0, 0, 0),
                          on_release=self._choose_avatar)
        paint_bg(cam_btn, ACCENT, [dp(20)])
        cam_btn.add_widget(Icon('camera', color=BG_APP, size_hint=(None, None),
                                 size=(dp(22), dp(22)),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        avatar_wrap.add_widget(cam_btn)

        body.add_widget(AnchorWrap(avatar_wrap))

        # ── Username (read-only, it's the account ID) ──
        body.add_widget(self._field_label("Your Name"))
        self.username_lbl = Label(text="", font_size=sp(16), bold=True,
                                   color=TEXT_PRIMARY, halign="left",
                                   size_hint_y=None, height=dp(28))
        self.username_lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        body.add_widget(self.username_lbl)
        body.add_widget(make_separator())

        # ── Bio (editable) ──
        body.add_widget(self._field_label("About"))
        self.bio_input = TextInput(multiline=False, background_normal='',
                                    background_color=(0, 0, 0, 0),
                                    foreground_color=TEXT_PRIMARY,
                                    hint_text="Add a few words about yourself",
                                    hint_text_color=TEXT_FAINT, cursor_color=ACCENT,
                                    font_size=sp(15), size_hint_y=None, height=dp(34),
                                    padding=[0, dp(6)])
        body.add_widget(self.bio_input)
        body.add_widget(make_separator())

        save_btn = Button(text="Save Changes", background_normal='',
                           background_color=(0, 0, 0, 0), color=BG_APP, bold=True,
                           font_size=sp(14), size_hint_y=None, height=dp(48),
                           on_release=self._save)
        paint_bg(save_btn, ACCENT, RADIUS_MD)
        body.add_widget(Widget(size_hint_y=None, height=dp(10)))
        body.add_widget(save_btn)

        body.add_widget(Widget())  # spacer

        root.add_widget(body)
        self.add_widget(root)

    def _field_label(self, text):
        lbl = Label(text=text, font_size=sp(11), color=ACCENT, bold=True,
                     halign="left", size_hint_y=None, height=dp(18))
        lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        return lbl

    def _go_back(self, *_):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'hub'

    def on_pre_enter(self):
        if store.exists('profile'):
            profile = store.get('profile')
            self.username_lbl.text = profile['username']
            self.bio_input.text = profile.get('bio', '')
            avatar_path = profile.get('avatar', '')
            if avatar_path and os.path.exists(avatar_path):
                self.avatar.set_image(avatar_path)
            else:
                self.avatar.set_letter(profile['username'][0].upper())

    def _choose_avatar(self, *_):
        pick_image(self._on_avatar_picked)

    def _on_avatar_picked(self, path):
        if path and os.path.exists(path):
            self.avatar.set_image(path)
            profile = store.get('profile')
            store.put('profile', username=profile['username'],
                      bio=profile.get('bio', ''), avatar=path)

    def _save(self, *_):
        profile = store.get('profile')
        new_bio = self.bio_input.text.strip()
        store.put('profile', username=profile['username'], bio=new_bio,
                  avatar=profile.get('avatar', ''))
        payload = json.dumps({"username": profile['username'], "bio": new_bio})
        UrlRequest(f"{FIREBASE_URL}users/{profile['username']}.json",
                   req_body=payload, method='PUT')
        self._go_back()


# ════════════════════════════════════════════════════════════════
#  APP
# ════════════════════════════════════════════════════════════════
class OrangeChatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ChatHubScreen(name='hub'))
        sm.add_widget(ExploreSocialScreen(name='explore'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ProfileScreen(name='profile'))
        return sm

    def on_start(self):
        request_storage_permissions()


if __name__ == "__main__":
    OrangeChatApp().run()
