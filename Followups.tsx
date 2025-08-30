// Followups.tsx
import { useEffect, useState } from "react";

export default function Followups({ sessionId, onComplete }: { sessionId: string, onComplete: (schema:any)=>void }) {
  const [q, setQ] = useState<string>("");
  const [field, setField] = useState<string>("");

  useEffect(() => {
    const es = new EventSource(`/api/intake/followups?session_id=${sessionId}`);
    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status === "need_followup") { setQ(data.question); setField(data.missing_field); }
      if (data.status === "complete") { onComplete(data.current_schema); es.close(); }
    };
    return () => es.close();
  }, [sessionId]);

  async function submitAnswer(answer: string) {
    const f = new FormData();
    f.append("session_id", sessionId);
    f.append("answer_text", answer);
    f.append("field", field);
    await fetch("/api/intake/answer", { method:"POST", body: f });
  }

  return q ? (
    <div className="space-y-3">
      <div className="font-medium">{q}</div>
      <AnswerInput onSubmit={submitAnswer}/>
    </div>
  ) : null;
}

function AnswerInput({ onSubmit }: { onSubmit:(t:string)=>void }) {
  const [val, setVal] = useState("");
  return (
    <div className="flex gap-2">
      <input className="border rounded p-2 flex-1" value={val} onChange={e=>setVal(e.target.value)} placeholder="Your answer…" />
      <button className="px-3 py-2 bg-purple-600 text-white rounded" onClick={()=>{onSubmit(val); setVal("");}}>Send</button>
    </div>
  );
}
