import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import toast from "react-hot-toast";

export default function Summary(){
  const {id} = useParams(); // id do atendimento
  const [data,setData]=useState<any>(null);
  const [loading,setLoading]=useState(false);

  async function load(){
    try{
      const d = await api(`/encounters/${id}`);
      // se ainda não houver suggestions, finalize uma vez
      if(!d.suggestions || Object.keys(d.suggestions).length===0){
        const f = await api(`/encounters/${id}/finalize`,{method:"POST"});
        setData(f);
      } else {
        setData(d);
      }
    }catch(e){
      // fallback: tenta finalizar
      const f = await api(`/encounters/${id}/finalize`,{method:"POST"});
      setData(f);
    }
  }

  useEffect(()=>{ load(); },[id]);

  async function sendFeedback(label:"agree"|"disagree"){
    try{
      setLoading(true);
      const res = await api(`/encounters/${id}/feedback`, {
        method: "POST",
        body: JSON.stringify({ label })
      });
      toast.success(label==="agree" ? "Feedback registrado: concordo" : "Feedback registrado: ajustei/discordo");
      // atualiza sugestões com feedback
      setData((prev:any)=> prev ? ({...prev, suggestions: res.suggestions}) : prev);
    }catch(e){
      console.error(e);
      toast.error("Falha ao enviar feedback");
    }finally{
      setLoading(false);
    }
  }

  async function downloadPDF(){
    const blob = await api(`/pdf/encounter/${id}`);
    const url = URL.createObjectURL(blob); const a = document.createElement("a");
    a.href=url; a.download=`atendimento_${id}.pdf`; a.click(); URL.revokeObjectURL(url);
  }

  if(!data) return null;
  const s = data.suggestions || {nao_farmacologicas:[], farmacologicas:[], alertas:[], rationale:[]};
  const fb = s.feedback || null;

  return <div className="container">
    <div className="card"><h2>Resumo & Sugestões</h2>
      <div className="card">
        <b>Não farmacológicas:</b><br/>{(s.nao_farmacologicas||[]).join("; ") || "—"}
      </div>
      <div className="card">
        <b>Farmacológicas:</b><br/>{(s.farmacologicas||[]).join("; ") || "—"}
      </div>
      <div className="card">
        <b>Alertas:</b><br/>{(s.alertas||[]).join("; ") || "—"}
      </div>
      <div className="card">
        <b>Por que sugerimos isso (rationale):</b>
        <ul style={{marginTop:8}}>
          {(s.rationale||[]).map((r:string, i:number)=> <li key={i}>{r}</li>)}
        </ul>
      </div>

      <div className="card">
        <b>Feedback do profissional</b>
        {fb ? (
          <div style={{marginTop:8}}>
            <span className="badge">Status: {fb.label === "agree" ? "Concordo" : "Ajustei/Discordo"}</span>
            {fb.ts && <span className="badge" style={{marginLeft:8}}>Em: {fb.ts}</span>}
          </div>
        ) : (
          <div className="row" style={{marginTop:8}}>
            <button className="btn" disabled={loading} onClick={()=>sendFeedback("agree")}>Concordo com as sugestões</button>
            <button className="btn ghost" disabled={loading} onClick={()=>sendFeedback("disagree")}>Ajustei/Discordo</button>
          </div>
        )}
      </div>

      <div className="row" style={{marginTop:12}}>
        <button className="btn" onClick={downloadPDF}>Gerar PDF (Atendimento)</button>
        <a className="btn ghost" href="/dashboard">Concluir</a>
      </div>
    </div>
  </div>;
}
