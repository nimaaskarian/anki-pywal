import json
import os
from aqt import mw, gui_hooks
from aqt.qt import QColor, QPalette, QTimer
from aqt.webview import AnkiWebView
from aqt.theme import theme_manager

PATH = os.path.expanduser("~/.cache/wal/colors.json")
_last = None
_c = None


def mix(a, b, t):
    a, b = QColor(a), QColor(b)
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
    )


def load():
    global _c
    try:
        with open(PATH) as f:
            d = json.load(f)
        bg, fg = d["special"]["background"], d["special"]["foreground"]
        accent = d["colors"]["color4"]
    except Exception:
        return False
    _c = {
        "bg": bg,
        "fg": fg,
        "accent": accent,
        "elev": mix(bg, fg, 0.06).name(),
        "inset": mix(bg, "#000000", 0.25).name(),
        "border": mix(bg, fg, 0.2).name(),
        "select": mix(bg, accent, 0.4).name(),
        "subtle": mix(fg, bg, 0.3).name(),
        "faint": mix(fg, bg, 0.55).name(),
    }
    return True


MARK = "/*theme_sync*/"


def rgbs(col):
    q = QColor(col)
    return f"{q.red()}, {q.green()}, {q.blue()}"


def bs_css():
    c = _c
    hi = mix(c["accent"], c["fg"], 0.15).name()
    hover = mix(c["elev"], c["fg"], 0.08).name()
    v = {
        "bs-body-color": c["fg"],
        "bs-body-bg": c["bg"],
        "bs-emphasis-color": c["fg"],
        "bs-heading-color": c["fg"],
        "bs-secondary-color": c["subtle"],
        "bs-tertiary-color": c["faint"],
        "bs-secondary-bg": c["elev"],
        "bs-tertiary-bg": c["inset"],
        "bs-border-color": c["border"],
        "bs-border-color-translucent": c["border"],
        "border-color": c["border"],
        "bs-link-color": c["accent"],
        "bs-link-hover-color": hi,
        "bs-primary": c["accent"],
        "bs-code-color": c["accent"],
        "bs-highlight-bg": c["select"],
        "bs-highlight-color": c["fg"],
        "bs-tooltip-bg": c["elev"],
        "bs-tooltip-color": c["fg"],
        "bs-white": c["fg"],
        "bs-black": c["bg"],
    }
    for k in (
        "body-color",
        "body-bg",
        "emphasis-color",
        "secondary-bg",
        "tertiary-bg",
        "link-color",
        "primary",
    ):
        v[f"bs-{k}-rgb"] = rgbs(v[f"bs-{k}"])
    for n, t in zip(
        range(100, 1000, 100), (0, 0.1, 0.25, 0.4, 0.55, 0.7, 0.8, 0.9, 0.95)
    ):
        v[f"bs-gray-{n}"] = mix(c["fg"], c["bg"], t).name()
    out = "".join(f"--{k}:{x} !important;" for k, x in v.items())
    btn = (
        f"--bs-btn-color:{c['fg']} !important;--bs-btn-bg:{c['elev']} !important;"
        f"--bs-btn-border-color:{c['border']} !important;"
        f"--bs-btn-hover-color:{c['fg']} !important;--bs-btn-hover-bg:{hover} !important;"
        f"--bs-btn-hover-border-color:{c['border']} !important;"
        f"--bs-btn-active-color:{c['fg']} !important;--bs-btn-active-bg:{c['select']} !important;"
        f"--bs-btn-disabled-color:{c['faint']} !important;--bs-btn-disabled-bg:{c['inset']} !important;"
    )
    return (
        ":root, body, .night-mode {" + out + "}"
        ".btn, .dropdown-item {" + btn + "}"
        f".dropdown-menu {{ background:{c['elev']} !important; color:{c['fg']} !important; }}"
    )


def css():
    c = _c
    hover = mix(c["elev"], c["fg"], 0.08).name()
    hi = mix(c["accent"], c["fg"], 0.15).name()
    sb_h = mix(c["border"], c["fg"], 0.15).name()
    sb_a = mix(c["border"], c["fg"], 0.3).name()
    prim_dis = mix(c["accent"], c["bg"], 0.5).name()
    v = {
        "canvas": c["bg"],
        "canvas-elevated": c["elev"],
        "canvas-inset": c["inset"],
        "canvas-overlay": c["elev"],
        "canvas-glass": c["elev"],
        "canvas-code": c["inset"],
        "fg": c["fg"],
        "fg-subtle": c["subtle"],
        "fg-faint": c["faint"],
        "fg-disabled": c["faint"],
        "fg-link": c["accent"],
        "border": c["border"],
        "border-subtle": c["border"],
        "border-strong": c["border"],
        "border-focus": c["accent"],
        "focus-color": c["accent"],
        "button-bg": c["elev"],
        "button-gradient-start": hover,
        "button-gradient-end": c["elev"],
        "button-hover-border": c["border"],
        "button-disabled": c["inset"],
        "button-primary-bg": c["accent"],
        "button-primary-gradient-start": hi,
        "button-primary-gradient-end": c["accent"],
        "button-primary-disabled": prim_dis,
        "scrollbar-bg": c["border"],
        "scrollbar-bg-hover": sb_h,
        "scrollbar-bg-active": sb_a,
        "highlight-bg": c["select"],
        "highlight-fg": c["fg"],
        "selected-bg": c["select"],
        "selected-fg": c["fg"],
    }
    body = "".join(f"--{k}:{x} !important;" for k, x in v.items())
    return ":root, body, .night-mode {" + body + "}" + bs_css()


def qss():
    c = _c
    return f"""{MARK}
QDialog, QMainWindow, QWidget#centralwidget {{ background:{c['bg']}; color:{c['fg']}; }}
QLabel, QCheckBox, QRadioButton, QGroupBox {{ color:{c['fg']}; }}
QPushButton, QToolButton {{ background:{c['elev']}; color:{c['fg']};
    border:1px solid {c['border']}; border-radius:4px; padding:4px 10px; }}
QPushButton:hover, QToolButton:hover {{ background:{c['select']}; }}
QPushButton:pressed {{ background:{c['inset']}; }}
QPushButton:disabled {{ color:{c['faint']}; }}
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
QListView, QTreeView, QTableView {{ background:{c['inset']}; color:{c['fg']};
    border:1px solid {c['border']}; selection-background-color:{c['select']};
    selection-color:{c['fg']}; }}
QComboBox QAbstractItemView {{ background:{c['elev']}; color:{c['fg']}; }}
QHeaderView::section {{ background:{c['elev']}; color:{c['fg']}; border:1px solid {c['border']}; }}
QTabWidget::pane {{ border:1px solid {c['border']}; }}
QTabBar::tab {{ background:{c['elev']}; color:{c['fg']}; padding:6px 12px; }}
QTabBar::tab:selected {{ background:{c['select']}; }}
QMenu {{ background:{c['elev']}; color:{c['fg']}; }}
QMenu::item:selected {{ background:{c['select']}; }}
QToolTip {{ background:{c['elev']}; color:{c['fg']}; border:1px solid {c['border']}; }}
"""


_orig = None


def recolor(sheet):
    c = _c
    hover = mix(c["elev"], c["fg"], 0.08).name()
    accent_hi = mix(c["accent"], c["fg"], 0.15).name()
    accent_lo = mix(c["accent"], c["fg"], 0.3).name()
    pairs = [
        ("background: #252525", f"background: {c['inset']}"),
        ("#252525", c["border"]),
        ("#363636", c["elev"]),
        ("#2c2c2c", c["elev"]),
        ("#fcfcfc", c["fg"]),
        ("#737373", c["faint"]),
        ("#3b82f6", c["accent"]),
        ("#141414", c["inset"]),
        ("#202020", c["border"]),
        ("#454545", c["border"]),
        ("#545454", mix(c["border"], c["fg"], 0.15).name()),
        ("#636363", mix(c["border"], c["fg"], 0.3).name()),
        ("rgb(25.1176470588%, 25.1176470588%, 25.1176470588%)", c["elev"]),
        ("rgb(29.0588235294%, 29.0588235294%, 29.0588235294%)", hover),
        ("rgb(15.0392156863%, 32.3333333333%, 81.0392156863%)", c["accent"]),
        ("rgb(18.3921568627%, 40.2745098039%, 88.2745098039%)", accent_hi),
        ("rgb(26.8039215686%, 51.862745098%, 92.8039215686%)", accent_lo),
        ("rgba(147, 197, 253, 0.5)", c["select"]),
        ("rgba(69, 69, 69, 0.5)", c["border"]),
    ]
    for old, new in pairs:
        sheet = sheet.replace(old, new)
    return sheet


def apply_palette():
    global _orig
    c = _c
    R = QPalette.ColorRole
    p = QPalette()
    for role, col in [
        (R.Window, c["bg"]),
        (R.WindowText, c["fg"]),
        (R.Base, c["elev"]),
        (R.AlternateBase, c["bg"]),
        (R.Text, c["fg"]),
        (R.Button, c["elev"]),
        (R.ButtonText, c["fg"]),
        (R.ToolTipBase, c["elev"]),
        (R.ToolTipText, c["fg"]),
        (R.PlaceholderText, c["faint"]),
        (R.Link, c["fg"]),
        (R.Highlight, c["select"]),
        (R.HighlightedText, c["fg"]),
    ]:
        p.setColor(role, QColor(col))
    mw.app.setPalette(p)

    sheet = mw.app.styleSheet()
    if MARK not in sheet:
        _orig = sheet
    base = _orig or ""
    out = recolor(base) if "QGroupBox" in base else base + qss()
    mw.app.setStyleSheet(out + "\n" + MARK)


def style_js():
    return (
        "(()=>{let s=document.getElementById('theme-sync');"
        "if(!s){s=document.createElement('style');s.id='theme-sync';document.head.appendChild(s)}"
        f"s.textContent={json.dumps(css())}}})()"
    )


def inject(w):
    if _c:
        w.eval(style_js())


gui_hooks.webview_did_inject_style_into_page.append(inject)


def apply(*_):
    if not _c:
        return
    apply_palette()
    js = style_js()
    for w in mw.app.allWidgets():
        if isinstance(w, AnkiWebView):
            w.eval(js)


def poll():
    global _last
    try:
        m = os.path.getmtime(PATH)
    except OSError:
        return
    if m != _last:
        _last = m
        if load():
            apply()


def on_content(web_content, context):
    if _c:
        web_content.head += f"<style id='theme-sync'>{css()}</style>"


_orig_apply_style = theme_manager.apply_style


def _patched_apply_style(*a, **k):
    _orig_apply_style(*a, **k)
    apply()


theme_manager.apply_style = _patched_apply_style
gui_hooks.profile_did_open.append(apply)

gui_hooks.webview_will_set_content.append(on_content)
gui_hooks.theme_did_change.append(apply)

timer = QTimer(mw)
timer.timeout.connect(poll)
timer.start(200)
