import { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import toast from "react-hot-toast";

export default function Questionnaire(){
  const {id} = useParams(); // id do atendimento
  const [step,setStep]=useState(0);
  const [ans,setAns]=useState<any>({
    motivo:"",
    duracao:"",
    dor:false, dor_intensidade:0,
    febre:false, febre_temp_max:null,
    adesao:"boa", // boa | irregular | ruim
    comorbidades:[], // ["ulcera_gastrica","asma","hipertensao","diabetes"]
    habitos:{ tabagismo:false, sono_ruim:false },
    sintomas:{
      tosse:false, coriza:false, dor_garganta:false, congestao_nasal:false,
      dor_cabeca:false, acidez:false, nausea:false, dor_lombar:false
    },
    sinais_alarme:[] // ["dispneia","dor_toracica","rigidez_nuca","confusao","sangramento_gi","vomitos_persistentes"]
  });

  function next(){ setStep(s=>s+1); savePartial(); }
  function prev(){ setStep(s=>Math.max(0,s-1)); savePartial(); }
  async function savePartial(){ await api(`/encounters/${id}`,{method:"PUT", body: JSON.stringify({data: ans})}); }
  async function finalize(){
    await savePartial();
    await api(`/encounters/${id}/finalize`,{method:"POST"});
    location.href = `/atendimento/resumo/${id}`;
  }

  const CK = (checked:boolean,onChange:any,label:string)=>
    <label style={{display:"inline-flex",alignItems:"center",gap:8, marginRight:14}}>
      <input type="checkbox" checked={checked} onChange={onChange}/> {label}
    </label>;

  const steps = [
    // 0
    <input key="motivo" placeholder="Motivo da consulta" value={ans.motivo} onChange={e=>setAns({...ans,motivo:e.target.value})}/>,

    // 1
    <input key="dur" placeholder="Duração dos sintomas (dias/sem)" value={ans.duracao} onChange={e=>setAns({...ans,duracao:e.target.value})}/>,

    // 2 - Dor
    <div key="dor">
      {CK(ans.dor, e=>setAns({...ans,dor:e.target.checked}), "Dor?")}
      {ans.dor && <input placeholder="Intensidade 0-10" onChange={e=>setAns({...ans,dor_intensidade: Number(e.target.value||0)})}/>}
    </div>,

    // 3 - Febre
    <div key="febre">
      {CK(ans.febre, e=>setAns({...ans,febre:e.target.checked}), "Febre?")}
      {ans.febre && <input placeholder="Temp. máxima (°C)" onChange={e=>setAns({...ans,febre_temp_max: e.target.value})}/>}
    </div>,

    // 4 - Sintomas (resp/cefaleia/digestivo/lombar)
    <div key="sintomas">
      <div><b>Respiratórios</b></div>
      {CK(ans.sintomas.tosse, e=>setAns({...ans, sintomas:{...ans.sintomas, tosse:e.target.checked}}), "Tosse")}
      {CK(ans.sintomas.coriza, e=>setAns({...ans, sintomas:{...ans.sintomas, coriza:e.target.checked}}), "Coriza")}
      {CK(ans.sintomas.dor_garganta, e=>setAns({...ans, sintomas:{...ans.sintomas, dor_garganta:e.target.checked}}), "Dor de garganta")}
      {CK(ans.sintomas.congestao_nasal, e=>setAns({...ans, sintomas:{...ans.sintomas, congestao_nasal:e.target.checked}}), "Congestão nasal")}
      <div style={{marginTop:8}}><b>Outros</b></div>
      {CK(ans.sintomas.dor_cabeca, e=>setAns({...ans, sintomas:{...ans.sintomas, dor_cabeca:e.target.checked}}), "Dor de cabeça")}
      {CK(ans.sintomas.acidez, e=>setAns({...ans, sintomas:{...ans.sintomas, acidez:e.target.checked}}), "Acidez/queimação")}
      {CK(ans.sintomas.nausea, e=>setAns({...ans, sintomas:{...ans.sintomas, nausea:e.target.checked}}), "Náusea")}
      {CK(ans.sintomas.dor_lombar, e=>setAns({...ans, sintomas:{...ans.sintomas, dor_lombar:e.target.checked}}), "Dor lombar")}
    </div>,

    // 5 - Comorbidades
    <div key="comorb">
      <div><b>Comorbidades</b></div>
      {CK(ans.comorbidades.includes("ulcera_gastrica"), e=>{
        const v=new Set(ans.comorbidades); e.target.checked? v.add("ulcera_gastrica"): v.delete("ulcera_gastrica");
        setAns({...ans,comorbidades:[...v]}); },"Úlcera/Gastrite")}
      {CK(ans.comorbidades.includes("asma"), e=>{
        const v=new Set(ans.comorbidades); e.target.checked? v.add("asma"): v.delete("asma");
        setAns({...ans,comorbidades:[...v]}); },"Asma")}
      {CK(ans.comorbidades.includes("hipertensao"), e=>{
        const v=new Set(ans.comorbidades); e.target.checked? v.add("hipertensao"): v.delete("hipertensao");
        setAns({...ans,comorbidades:[...v]}); },"Hipertensão")}
      {CK(ans.comorbidades.includes("diabetes"), e=>{
        const v=new Set(ans.comorbidades); e.target.checked? v.add("diabetes"): v.delete("diabetes");
        setAns({...ans,comorbidades:[...v]}); },"Diabetes")}
    </div>,

    // 6 - Hábitos e Aderência
    <div key="habitos">
      <div><b>Hábitos</b></div>
      {CK(ans.habitos.tabagismo, e=>setAns({...ans,habitos:{...ans.habitos,tabagismo:e.target.checked}}), "Tabagismo")}
      {CK(ans.habitos.sono_ruim, e=>setAns({...ans,habitos:{...ans.habitos,sono_ruim:e.target.checked}}), "Sono ruim")}
      <div style={{marginTop:8}}><b>Aderência aos medicamentos em uso</b></div>
      <select value={ans.adesao} onChange={e=>setAns({...ans,adesao:e.target.value})}>
        <option value="boa">Boa</option>
        <option value="irregular">Irregular</option>
        <option value="ruim">Ruim</option>
      </select>
    </div>,

    // 7 - Sinais de alarme
    <div key="alarme">
      <div><b>Sinais de alarme</b></div>
      {CK(ans.sinais_alarme.includes("dispneia"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("dispneia"): v.delete("dispneia");
        setAns({...ans,sinais_alarme:[...v]}); },"Dispneia intensa")}
      {CK(ans.sinais_alarme.includes("dor_toracica"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("dor_toracica"): v.delete("dor_toracica");
        setAns({...ans,sinais_alarme:[...v]}); },"Dor torácica")}
      {CK(ans.sinais_alarme.includes("rigidez_nuca"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("rigidez_nuca"): v.delete("rigidez_nuca");
        setAns({...ans,sinais_alarme:[...v]}); },"Rigidez de nuca")}
      {CK(ans.sinais_alarme.includes("confusao"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("confusao"): v.delete("confusao");
        setAns({...ans,sinais_alarme:[...v]}); },"Confusão/alteração de consciência")}
      {CK(ans.sinais_alarme.includes("sangramento_gi"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("sangramento_gi"): v.delete("sangramento_gi");
        setAns({...ans,sinais_alarme:[...v]}); },"Sangramento gastrointestinal")}
      {CK(ans.sinais_alarme.includes("vomitos_persistentes"), e=>{
        const v=new Set(ans.sinais_alarme); e.target.checked? v.add("vomitos_persistentes"): v.delete("vomitos_persistentes");
        setAns({...ans,sinais_alarme:[...v]}); },"Vômitos persistentes")}
    </div>,
  ];

  return <div className="container">
    <div className="card"><h2>Questionário Interativo</h2>
      <div className="grid">{steps[step]}</div>
      <div className="row" style={{marginTop:12}}>
        <button className="btn" onClick={prev} disabled={step===0}>Voltar</button>
        {step < steps.length-1 ? <button className="btn" onClick={next}>Próximo</button>
          : <button className="btn" onClick={finalize}>Finalizar</button>}
      </div>
    </div>
  </div>;
}
