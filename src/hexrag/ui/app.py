"""Optional minimal Gradio UI: ingest text/files and chat with retrieval.

Mounted only when ui.enabled is true. Kept deliberately thin — the API is the
primary surface. Install with: uv sync --extra ui"""

from __future__ import annotations

from pathlib import Path

import gradio as gr
from fastapi import FastAPI
from injector import Injector
from llama_index.core.llms import ChatMessage, MessageRole

from hexrag.services.chat import ChatService
from hexrag.services.ingest import IngestService


class HexRagUI:
    def __init__(self, injector: Injector) -> None:
        self._chat = injector.get(ChatService)
        self._ingest = injector.get(IngestService)

    def _answer(self, message: str, history: list) -> str:
        messages = []
        for turn in history:
            messages.append(ChatMessage(role=MessageRole.USER, content=turn[0]))
            messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=turn[1]))
        messages.append(ChatMessage(role=MessageRole.USER, content=message))
        completion = self._chat.chat(messages, use_context=True)
        sources = "\n".join(
            f"- {s.file_name or s.doc_id}: {s.text[:120]}" for s in completion.sources
        )
        suffix = f"\n\n**Sources:**\n{sources}" if sources else ""
        return completion.response + suffix

    def _upload(self, file_path: str | None) -> str:
        if not file_path:
            return "No file selected."
        p = Path(file_path)
        docs = self._ingest.ingest_file(p.name, p)
        return f"Ingested {p.name} ({len(docs)} document(s))."

    def _build(self) -> gr.Blocks:
        with gr.Blocks(title="hexrag") as blocks:
            gr.Markdown("# hexrag\nIngest a document, then ask grounded questions.")
            with gr.Row():
                upload = gr.File(label="Ingest a file", type="filepath")
                status = gr.Textbox(label="Status", interactive=False)
            upload.upload(self._upload, inputs=upload, outputs=status)
            gr.ChatInterface(self._answer)
        return blocks

    def mount_in_app(self, app: FastAPI, path: str) -> None:
        gr.mount_gradio_app(app, self._build(), path=path)
