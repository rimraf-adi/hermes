from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, ConditionalContainer, Window
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.controls import FormattedTextControl
import sys, os


def Hermes(filename=None):
    # Load file content if given
    text = ""
    if filename:
        try:
            with open(filename, "r") as f:
                text = f.read()
        except FileNotFoundError:
            pass

    # --- Main text area
    textarea = TextArea(
        text=text,
        multiline=True,
        line_numbers=True,
        wrap_lines=False,
    )

    # --- Status bar
    status = TextArea(
        text=f" -- INSERT -- | {filename or '[No Name]'} ",
        style="class:status",
        height=1,
        multiline=False,
        wrap_lines=False,
        focusable=False,
    )

    # --- File browser state
    cwd = os.getcwd()
    files = os.listdir(cwd)
    selected_index = {"value": 0}
    show_file_browser = {"value": False}

    def get_file_lines():
        lines = []
        for i, f in enumerate(files):
            if i == selected_index["value"]:
                lines.append([("reverse", f" {f} ")])
            else:
                lines.append([("", f" {f} ")])
        return lines


    file_browser_control = FormattedTextControl(get_file_lines)
    file_browser = Window(
        content=file_browser_control,
        width=30,
        style="class:filepane",
        wrap_lines=False,
    )

    # --- Key bindings
    kb = KeyBindings()

    @kb.add("c-p")  # Ctrl-P = save
    def save_file(event):
        if filename:
            with open(filename, "w") as f:
                f.write(textarea.text)
            status.text = f" Saved {filename} "
        else:
            status.text = " No filename provided "

    @kb.add("c-q")  # Ctrl-Q = quit
    def quit_app(event):
        event.app.exit()

    @kb.add("c-v")  # Ctrl-V = toggle vim mode
    def toggle_vim(event):
        app = event.app
        if app.editing_mode == EditingMode.EMACS:
            app.editing_mode = EditingMode.VI
            status.text = f" -- VIM MODE -- | {filename or '[No Name]'} "
        else:
            app.editing_mode = EditingMode.EMACS
            status.text = f" -- INSERT -- | {filename or '[No Name]'} "

    @kb.add("c-b")  # Ctrl-B = toggle file browser
    def toggle_file_browser(event):
        show_file_browser["value"] = not show_file_browser["value"]
        if show_file_browser["value"]:
            status.text = f" -- FILES OPEN -- | {filename or '[No Name]'} "
        else:
            status.text = f" -- INSERT -- | {filename or '[No Name]'} "

    # --- Navigation inside file browser
    @kb.add("up")
    def move_up(event):
        if show_file_browser["value"] and selected_index["value"] > 0:
            selected_index["value"] -= 1

    @kb.add("down")
    def move_down(event):
        if show_file_browser["value"] and selected_index["value"] < len(files) - 1:
            selected_index["value"] += 1

    @kb.add("enter")
    def open_file(event):
        if show_file_browser["value"]:
            fname = files[selected_index["value"]]
            path = os.path.join(cwd, fname)
            if os.path.isfile(path):
                with open(path, "r", errors="ignore") as f:
                    textarea.text = f.read()
                status.text = f" -- OPENED {fname} -- "
            else:
                status.text = f" {fname} is not a file "

    # --- Layout
    body = VSplit([
        ConditionalContainer(
            content=file_browser,
            filter=Condition(lambda: show_file_browser["value"]),
        ),
        textarea,
    ])

    root_container = HSplit([body, status])

    layout = Layout(root_container)

    style = Style.from_dict({
        "status": "reverse",
        "filepane": "bg:#222222 #aaaaaa",
    })

    # --- Application
    return Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
        style=style,
        editing_mode=EditingMode.EMACS,  # default
    )


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = Hermes(filename)
    app.run()
