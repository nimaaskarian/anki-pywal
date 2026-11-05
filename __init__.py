import json
import os
from aqt import mw, gui_hooks
from aqt.qt import QColor, QPalette, QTimer
from aqt.webview import AnkiWebView

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


def apply_palette():
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
    mw.app.setStyleSheet(mw.app.styleSheet().split(MARK)[0] + qss())


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


gui_hooks.webview_will_set_content.append(on_content)
gui_hooks.theme_did_change.append(apply)

timer = QTimer(mw)
timer.timeout.connect(poll)
timer.start(200)
