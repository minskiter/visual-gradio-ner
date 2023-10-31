import gradio as gr
import json
import tempfile
from typing import Union
from utils import convert_bmes_to_span

data1 = []
data2 = []
diff = []
page_size = 10
page = 0


def convert_bmes_to_entities(obj, no=None):
    if len(obj["text"]) == 0:
        return None
    return {
        "no": no,
        "text": "".join(obj["text"]),
        "entities": list(
            {"start": l, "end": r + 1, "entity": label}
            for l, r, label in convert_bmes_to_span(obj["label"])
        ),
    }


def read_bmes(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            if len(obj["text"]) > 0:
                data.append(convert_bmes_to_entities(obj, i + 1))
    return data


def get_data(file: tempfile._TemporaryFileWrapper):
    if file is None:
        return show_data()
    global data1, page, data2, diff
    diff = []
    if isinstance(file, list) and len(file) == 2:
        f1, f2 = list(f.name for f in file)[:2]
        data1 = read_bmes(f1)
        data2 = read_bmes(f2)
        assert len(data1) == len(data2)
        for i, j in zip(data1, data2):
            i_entities = set((k["start"], k["end"], k["entity"]) for k in i["entities"])
            j_entities = set((k["start"], k["end"], k["entity"]) for k in j["entities"])
            if i_entities != j_entities:
                diff.append((i, j))
    else:
        if isinstance(file, list):
            diff = read_bmes(file[0].name)
            page = -1
    return show_data()


def show_data():
    global page, page_size, diff
    if len(diff) == 0:
        return list(gr.HighlightedText(visible=False) for _ in range(page_size * 2))
    if not isinstance(diff[0], tuple):
        l = page * page_size
        r = (page + 1) * page_size
        samples = diff[l:r]
        padding = page_size * 2 - len(samples)
        return list(
            gr.HighlightedText(visible=True, value=i, label=f"No.{i['no']}")
            for i in samples
        ) + list(gr.HighlightedText(visible=False) for i in range(padding))
    else:
        l = page * page_size
        r = (page + 1) * page_size
        samples = diff[l:r]
        return (
            list(
                gr.HighlightedText(visible=True, value=i[0], label=f"No.{i[0]['no']}")
                for i in samples
            )
            + list(
                gr.HighlightedText(visible=False)
                for _ in range(page_size - len(samples))
            )
            + list(
                gr.HighlightedText(visible=True, value=i[1], label=f"No.{i[1]['no']}")
                for i in samples
            )
            + list(
                gr.HighlightedText(visible=False)
                for _ in range(page_size - len(samples))
            )
        )


def next_page():
    global page, page_size, diff
    if page + 1 < len(diff) / page_size:
        page += 1
    return show_data()


def pre_page():
    global page
    if page > 0:
        page -= 1
    return show_data()


samples1 = []
samples2 = []

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=4):
            for i in range(page_size):
                samples1.append(gr.HighlightedText(visible=False))
        with gr.Column(scale=4):
            for i in range(page_size):
                samples2.append(gr.HighlightedText(visible=False))
        with gr.Column(scale=1):
            in1 = gr.File(label="Diff files", file_count="multiple")
            nxt = gr.Button("Next")
            pre = gr.Button("Prev")

    in1.change(fn=get_data, inputs=in1, outputs=samples1 + samples2)
    nxt.click(fn=next_page, outputs=samples1 + samples2)
    pre.click(fn=pre_page, outputs=samples1 + samples2)

demo.launch()
