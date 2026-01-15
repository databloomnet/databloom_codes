import gradio as gr

def hello(name: str) -> str:
    name = (name or "").strip() or "there"
    return f"Hello, {name}! 👋"

demo = gr.Interface(
    fn=hello,
    inputs=gr.Textbox(label="Your name"),
    outputs=gr.Textbox(label="Response"),
    title="DataBloom Gradio Demo",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
