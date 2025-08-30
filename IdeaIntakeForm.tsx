// IdeaIntakeForm.tsx
import { useState } from "react";

export default function IdeaIntakeForm({ onStarted }: { onStarted: (sid:string)=>void }) {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);

  async function start() {
    const form = new FormData();
    form.append("initial_text", text);
    const res = await fetch("/api/intake/start", { method:"POST", body: form });
    const data = await res.json();
    const sid = data.session_id;
    if (file) {
      const u = new FormData();
      u.append("session_id", sid);
      u.append("file", file);
      await fetch("/api/intake/upload", { method: "POST", body: u });
    }
    onStarted(sid);
  }

  return (
    <div className="space-y-3">
      <textarea
        className="w-full border rounded p-3"
        placeholder="Describe your idea in 3–5 lines…"
        value={text}
        onChange={e=>setText(e.target.value)}
      />
      <input type="file" onChange={e=>setFile(e.target.files?.[0] ?? null)} />
      <button className="px-4 py-2 rounded bg-purple-600 text-white" onClick={start}>
        Start Validation
      </button>
    </div>
  );
}