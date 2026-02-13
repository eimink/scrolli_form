import filecmp
import os
import threading

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
        name = gr.Textbox(label="Keep me informed about Skrolli IE", elem_id="name_textbox", placeholder="heikki@hakkeri.leet")
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

# Progress display page
with gr.Blocks(theme=theme, css=css) as progress_display:
    gr.Markdown("# INTERNATIONAL EDITION PLEDGES")
    
    with gr.Column(scale=1, elem_classes=["progress_container"]):
        with gr.Column(scale=0, elem_classes=["progress_content"]):
        
            pixel_image = gr.Image(
                value="longer_pixels.png",
                interactive=False,
                show_label=False,
                container=False,
                visible=False,
            )
            
            vertical_bar = gr.HTML()
            
            def get_progress():
                total = sum_values_from_files("./output")
                fill_percentage = min((total / 10000) * 100, 100)
                html = f"""
                <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
                    <div style="width: 40vw; height: 85vh; background: #0b0b0b; border: 2px solid #000; position: relative; overflow: hidden;">
                        <div style="width: 100%; height: {fill_percentage}%; background-image: url('data:image/png;base64,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'); background-size: cover; position: absolute; bottom: 0; transition: height 0.3s ease;"></div>
                    </div>
                </div>
                """
                return f"{total}€", html
            
            amount = gr.Textbox(
                value=f"{initial_total}€",
                show_label=False,
                container=False,
                interactive=False,
                elem_id="progress_amount",
            )
            
            # Create a timer that periodically updates the progress (every 5 seconds)
            timer = gr.Timer(value=5)
            
            # Load progress on page load
            progress_display.load(fn=get_progress, outputs=[amount, vertical_bar])
            
            # Also update on timer tick (periodic refresh for iframe rotation)
            timer.tick(fn=get_progress, outputs=[amount, vertical_bar])

            

if __name__ == "__main__":
    port1 = int(os.environ.get("PORT", "7860"))
    port2 = int(os.environ.get("PROGRESS_PORT", "7861"))
    
    def run_submission():
        demo.launch(server_name="0.0.0.0", server_port=port1, share=False)
    
    def run_progress():
        progress_display.launch(server_name="0.0.0.0", server_port=port2, share=False)
    
    t1 = threading.Thread(target=run_submission, daemon=True)
    t2 = threading.Thread(target=run_progress, daemon=True)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()