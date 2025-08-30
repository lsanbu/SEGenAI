// VoiceRecorder.tsx
import { useRef, useState } from "react";

export default function VoiceRecorder({ sessionId }: { sessionId: string }) {
  const [rec, setRec] = useState<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    setRec(recorder);
    chunks.current = [];
    recorder.ondataavailable = (e) => chunks.current.push(e.data);
    recorder.onstop = async () => {
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      const f = new File([blob], "idea.webm", { type: "audio/webm" });
      const form = new FormData();
      form.append("session_id", sessionId);
      form.append("file", f);
      await fetch("/api/intake/upload", { method: "POST", body: form });
    };
    recorder.start();
  }

  function stop() { rec?.stop(); }

  return (
    <div className="flex gap-2">
      <button className="px-3 py-2 bg-green-600 text-white rounded" onClick={start}>Record</button>
      <button className="px-3 py-2 bg-gray-700 text-white rounded" onClick={stop}>Stop</button>
    </div>
  );
}
