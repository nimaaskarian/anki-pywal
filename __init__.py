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


def css():
    c = _c
    v = {
        "canvas": c["bg"],
        "canvas-elevated": c["elev"],
        "canvas-inset": c["inset"],
        "fg": c["fg"],
        "fg-subtle": c["subtle"],
        "fg-faint": c["faint"],
        "border": c["border"],
        "border-subtle": c["border"],
        "button-bg": c["elev"],
        "button-gradient-start": c["elev"],
        "button-gradient-end": c["elev"],
        "button-disabled": c["inset"],
        "highlight-bg": c["select"],
        "highlight-fg": c["fg"],
        "selected-bg": c["select"],
        "selected-fg": c["fg"],
    }
    body = "".join(f"--{k}:{x};" for k, x in v.items())
    return ":root, :root.night-mode {" + body + "}"


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
        (R.Window, c["bg"]), (R.WindowText, c["fg"]),
        (R.Base, c["elev"]), (R.AlternateBase, c["bg"]),
        (R.Text, c["fg"]), (R.Button, c["elev"]), (R.ButtonText, c["fg"]),
        (R.ToolTipBase, c["elev"]), (R.ToolTipText, c["fg"]),
        (R.PlaceholderText, c["faint"]), (R.Link, c["fg"]),
        (R.Highlight, c["select"]), (R.HighlightedText, c["fg"]),
    ]:
        p.setColor(role, QColor(col))
    mw.app.setPalette(p)

    sheet = mw.app.styleSheet()
    if MARK not in sheet:
        _orig = sheet
    base = _orig or ""
    out = recolor(base) if "QGroupBox" in base else base + qss()
    mw.app.setStyleSheet(out + "\n" + MARK)

def apply(*_):
    if not _c:
        return
    apply_palette()
    js = (
        "(()=>{let s=document.getElementById('theme-sync');"
        "if(!s){s=document.createElement('style');s.id='theme-sync';document.head.appendChild(s)}"
        f"s.textContent={json.dumps(css())}}})()"
    )
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
