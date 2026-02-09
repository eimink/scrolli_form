import filecmp
import os

import gradio as gr
from pathlib import Path
import re

css = open("style.css").read()
theme = gr.themes.Monochrome(
    primary_hue="fuchsia",
    secondary_hue="stone",
    neutral_hue=gr.themes.Color(c100="rgba(255, 255, 255, 1)", c200="rgba(255, 255, 255, 1)", c300="rgba(61.28077889901622, 0, 71.9383056640625, 1)", c400="rgba(255, 255, 255, 1)", c50="rgba(255, 255, 255, 1)", c500="#ff00a6", c600="rgba(255, 255, 255, 1)", c700="rgba(0, 0, 0, 1)", c800="rgba(0, 0, 0, 1)", c900="rgba(0, 0, 0, 1)", c950="rgba(0, 0, 0, 1)"),
)

def sum_values_from_files(folder):
    """
    Read all files in a folder.
    Each file must contain a single line: email,value
    Returns:
        total_sum (float)
    """
    folder = Path(folder)
    total = 0.0
    for path in folder.iterdir():
        if not path.is_file():
            continue
        line = path.read_text(encoding="utf-8").strip()
        if not line:
            continue
        try:
            _, value = line.split(",", 1)
            total += float(value)
        except ValueError:
            raise ValueError(f"Invalid format in {path.name}: {line}")
    return total

def save_indexed_texts(texts, folder, prefix="pledge", extension=".txt"):
    """
    Save text strings as index-numbered files, continuing from
    the highest existing index in the folder.

    Existing files must match: {prefix}_{index}{extension}
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+){re.escape(extension)}$")
    max_index = -1
    for path in folder.iterdir():
        if not path.is_file():
            continue
        match = pattern.match(path.name)
        if match:
            max_index = max(max_index, int(match.group(1)))
    start_index = max_index + 1
    for i, text in enumerate(texts, start=start_index):
        (folder / f"{prefix}_{i}{extension}").write_text(text, encoding="utf-8")

def submit(name, slider):
    save_indexed_texts([f"{name}, {slider}"], "./output")
    total = sum_values_from_files("./output")
    return total, f"{total}€"

def submit_fn(value):
    return f"Submit: {value}€"

initial_total = sum_values_from_files("./output")

with gr.Blocks(theme=theme, css=css) as demo:
    logo = gr.Image(
        value="logo.png",
        interactive=False,
        show_label=False,
        container=False,
        elem_id="logo",
    )
    side_l = gr.Image(
        value="longer_pixels.png",
        interactive=False,
        show_label=False,
        container=False,
        elem_id="side_l",
        elem_classes=["side-theme"]
    )
    side_r = gr.Image(
        value="longer_pixels.png",
        interactive=False,
        show_label=False,
        container=False,
        elem_id="side_r",
        elem_classes=["side-theme"]
    )

    with gr.Row(elem_id="progress_wrapper", equal_height=False):
        progress = gr.Slider(
            interactive=False,
            value=initial_total,
            minimum=0,
            maximum=10000,
            label="Target for International Edition",
            elem_id="progress_slider",
            elem_classes=["slider-theme", "slider-only"],
        )

        progress_display = gr.Textbox(
            value=f"{initial_total}€",
            show_label=False,
            container=False,
            interactive=False,
            elem_id="progress_value_display",
            elem_classes=["slider-theme", "slider-only"],
        )    

    slider = gr.Slider(
        value=20,
        minimum=15,
        maximum=500,
        step=5,
        label="How much would you pay for the International Edition?",
        elem_id="pledge_slider",
        elem_classes=["slider-theme", "slider-only"],
    )

    with gr.Row(elem_id="preset_buttons"):
        pre_1 = gr.Button(value="Preset: 20€", elem_classes=["preset_button", "generic_button_class"])
        pre_2 = gr.Button(value="Preset: 30€", elem_classes=["preset_button", "generic_button_class"])
        pre_3 = gr.Button(value="Preset: 40€", elem_classes=["preset_button", "generic_button_class"])
        pre_4 = gr.Button(value="Preset: 50€", elem_classes=["preset_button", "generic_button_class"])

    pre_1.click(fn=lambda: 20, outputs=slider)
    pre_2.click(fn=lambda: 30, outputs=slider)
    pre_3.click(fn=lambda: 40, outputs=slider)
    pre_4.click(fn=lambda: 50, outputs=slider)


    #output = gr.Textbox(label="Output Box")
    with gr.Row():
        name = gr.Textbox(label="Keep me informed about Scrolli IE", elem_id="name_textbox", placeholder="heikki@hakkeri.leet")
        greet_btn = gr.Button(value="Submit: 20€", elem_id="greet_btn", elem_classes=["preset_button", "generic_button_class"])
        # 🔁 update button label when slider changes
        slider.change(
            fn=submit_fn,
            inputs=slider,
            outputs=greet_btn,
        )
        greet_btn.click(
            fn=submit,
            inputs=[name, slider],
            outputs=[progress, progress_display],
            api_name="submit",
        )

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", "7860")))