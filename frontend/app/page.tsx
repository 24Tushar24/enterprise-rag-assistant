"use client";

import { useEffect, useRef, useState } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("Home");
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [documents, setDocuments] = useState<any[]>([]);
  const [messages, setMessages] = useState<
    {
      role: "user" | "assistant";
      content: string;
      citations?: {
        filename: string;
        page: number;
      }[];
    }[]
  >([]);

  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const knowledgeBaseRef = useRef<HTMLDivElement>(null);

  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://localhost:8000/documents");
      const data = await response.json();

      if (response.ok) {
        setDocuments(data.documents);
      }
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, chatLoading]);

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      setUploadMessage("Only PDF files are supported.");
      return;
    }

    try {
      setUploading(true);
      setUploadMessage("");

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/documents", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadMessage(`${data.filename} indexed successfully.`);
      await fetchDocuments();
    } catch (error) {
      setUploadMessage(
        error instanceof Error ? error.message : "Upload failed.",
      );
    } finally {
      setUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || chatLoading) return;

    const userMessage = input.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setInput("");
    setChatLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: userMessage,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to get response");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          citations: data.citations || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error instanceof Error ? error.message : "Something went wrong.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f7f7f8] text-[#202123]">
      <div className="flex h-screen overflow-hidden">
        {/* ================= SIDEBAR ================= */}
        <aside className="hidden w-[220px] flex-col border-r border-[#e5e5e5] bg-white md:flex">
          {/* Logo */}
          <div className="flex h-[64px] items-center gap-3 border-b border-[#eeeeee] px-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#202123] text-sm font-semibold text-white">
              R
            </div>

            <div>
              <p className="text-sm font-semibold">RAG Assistant</p>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 px-3 py-5">
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
              Workspace
            </p>

            <button
              onClick={() => {
                setActiveTab("Home");

                knowledgeBaseRef.current?.scrollTo({
                  top: 0,
                  behavior: "smooth",
                });
              }}
              className={`mb-1 flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${
                activeTab === "Home"
                  ? "bg-[#eeeeef] font-medium"
                  : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              <span>⌂</span>
              Home
            </button>

            <button
              onClick={() => {
                setActiveTab("Documents");
                document.getElementById("documents-section")?.scrollIntoView({
                  behavior: "smooth",
                });
              }}
              className={`flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${
                activeTab === "Documents"
                  ? "bg-[#eeeeef] font-medium"
                  : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              <span>▣</span>
              Documents
            </button>
          </div>

          {/* Bottom */}
          <div className="border-t border-[#eeeeee] p-4">
            <div className="flex items-center gap-3 rounded-lg bg-[#f7f7f8] p-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#dedede] text-xs font-semibold">
                AI
              </div>

              <div>
                <p className="text-xs font-medium">AI Workspace</p>
              </div>
            </div>
          </div>
        </aside>

        {/* ================= KNOWLEDGE BASE ================= */}
        <section
          id="knowledge-base"
          className="flex w-full flex-col border-r border-[#e5e5e5] bg-white md:w-[43%]"
        >
          {/* Header */}
          <div className="flex h-[64px] items-center justify-between border-b border-[#eeeeee] px-6">
            <div>
              <h1 className="text-sm font-semibold">Knowledge Base</h1>
              <p className="text-[11px] text-gray-400">
                Manage your enterprise documents
              </p>
            </div>

            <button
              onClick={() => document.getElementById("pdf-upload")?.click()}
              className="rounded-md bg-[#202123] px-3 py-2 text-xs font-medium text-white transition hover:bg-[#343538] cursor-pointer"
            >
              + Add New
            </button>
          </div>

          <div ref={knowledgeBaseRef} className="flex-1 overflow-y-auto p-6">
            {/* Upload Box */}
            <div className="mb-7">
              <p className="mb-2 text-xs font-medium text-gray-600">
                Upload Knowledge
              </p>

              <div className="group cursor-pointer rounded-xl border border-dashed border-[#d5d5d5] bg-[#fafafa] p-8 text-center transition hover:border-[#999] hover:bg-[#f7f7f7]">
                <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm">
                  ↑
                </div>

                <p className="text-sm font-medium">
                  Click to upload or drag and drop
                </p>

                <p className="mt-1 text-[11px] text-gray-400">
                  PDF files only · Max 10MB
                </p>

                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleUpload}
                  className="hidden"
                  id="pdf-upload"
                />

                <label
                  htmlFor="pdf-upload"
                  className="mt-4 inline-block cursor-pointer rounded-md border border-[#dddddd] bg-white px-4 py-2 text-xs font-medium shadow-sm transition hover:bg-gray-50"
                >
                  {uploading ? "Uploading..." : "Browse Files"}
                </label>

                {uploadMessage && (
                  <p className="mt-3 text-[11px] text-gray-500">
                    {uploadMessage}
                  </p>
                )}
              </div>
            </div>

            {/* DOCUMENTS */}
            <div id="documents-section">
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-700">Documents</p>
                  <p className="text-[10px] text-gray-400">Indexed knowledge</p>
                </div>

                <span className="rounded-full bg-[#f0f0f0] px-2 py-1 text-[10px] text-gray-500">
                  {documents.length} files
                </span>
              </div>

              {documents.map((document) => (
                <div
                  key={document.document_id}
                  className="mb-2 flex items-center justify-between rounded-lg border border-[#eeeeee] bg-white p-3 transition hover:border-[#d5d5d5]"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-[#f2f2f2] text-sm">
                      📄
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-xs font-medium">
                        {document.filename}
                      </p>

                      <p className="mt-1 text-[10px] text-gray-400">
                        {document.pages?.length || 0} pages · PDF
                      </p>
                    </div>
                  </div>

                  <span className="ml-3 shrink-0 rounded-full bg-[#e9f7ef] px-2 py-1 text-[9px] font-medium text-[#287a4d]">
                    Indexed
                  </span>
                </div>
              ))}

              {documents.length === 0 && (
                <p className="py-6 text-center text-xs text-gray-400">
                  No documents indexed yet.
                </p>
              )}
            </div>
          </div>
        </section>

        {/* ================= AI ASSISTANT ================= */}
        <section className="flex min-w-0 flex-1 flex-col bg-[#fbfbfb]">
          {/* Assistant Header */}
          <div className="flex h-[64px] items-center justify-between border-b border-[#eeeeee] bg-white px-6">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#202123] text-sm text-white">
                ✦
              </div>

              <div>
                <p className="text-sm font-semibold">AI Assistant</p>

                <div className="mt-0.5 flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  <span className="text-[10px] text-gray-400">Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto px-5 py-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-5 flex gap-3 ${
                  message.role === "user" ? "justify-end" : ""
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#e8e8e8] text-xs">
                    ✦
                  </div>
                )}

                <div
                  className={`max-w-[85%] ${
                    message.role === "user" ? "items-end" : ""
                  }`}
                >
                  <div
                    className={`rounded-xl px-4 py-3 shadow-sm ${
                      message.role === "user"
                        ? "bg-[#202123] text-white"
                        : "border border-[#e8e8e8] bg-white text-gray-700"
                    }`}
                  >
                    <p className="text-xs leading-5">{message.content}</p>
                  </div>

                  {message.role === "assistant" &&
                    message.citations &&
                    message.citations.length > 0 && (
                      <div className="mt-2 rounded-lg border border-[#e8e8e8] bg-white p-3">
                        <p className="mb-2 text-[9px] font-semibold uppercase tracking-wider text-gray-400">
                          Sources
                        </p>

                        {message.citations.map((citation, citationIndex) => (
                          <div
                            key={citationIndex}
                            className="mb-2 flex items-center gap-2 last:mb-0"
                          >
                            <span className="text-xs">📄</span>

                            <div>
                              <p className="text-[10px] font-medium text-gray-700">
                                {citation.filename}
                              </p>

                              <p className="text-[9px] text-gray-400">
                                Page {citation.page}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))}

            {chatLoading && (
              <div className="flex gap-3">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#e8e8e8] text-xs">
                  ✦
                </div>

                <div className="rounded-xl border border-[#e8e8e8] bg-white px-4 py-3 shadow-sm">
                  <p className="text-xs text-gray-400">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[#eeeeee] bg-white p-4">
            <div className="mx-auto max-w-3xl">
              <div className="flex items-end gap-2 rounded-xl border border-[#dddddd] bg-white p-2 shadow-sm transition focus-within:border-[#999]">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="Ask a question about your documents..."
                  rows={1}
                  className="max-h-32 flex-1 resize-none bg-transparent px-2 py-2 text-xs text-gray-700 outline-none placeholder:text-gray-400"
                />

                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading || !input.trim()}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#202123] text-sm text-white transition hover:bg-[#343538]"
                >
                  ↑
                </button>
              </div>

              <p className="mt-2 text-center text-[9px] text-gray-400">
                AI responses are grounded in your indexed documents.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
