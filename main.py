from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style
import sys

def editor_app(filename=None):
    
    text = ""
    if filename:
        try:
            with open(filename, "r") as f:
                text = f.read()
        except FileNotFoundError:
            pass

    # Main editing area
    textarea = TextArea(
        text=text,
        multiline=True,
        line_numbers=True,
        wrap_lines=False,
    )

    # Status bar
    status = TextArea(
        text=f" -- INSERT -- | {filename or '[No Name]'} ",
        style="class:status",
        height=1,
        multiline=False,
        wrap_lines=False,
        focusable=False
    )

    # Key bindings
    kb = KeyBindings()

    @kb.add("c-p")  # Ctrl-S = save
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

    # Layout
    root_container = HSplit([
        textarea,
        status
    ])

    layout = Layout(root_container)

    style = Style.from_dict({
        "status": "reverse",
    })

    # Application
    return Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
        style=style
    )

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = editor_app(filename)
    app.run()
