import { useState } from "react";
import { api } from "../lib/api";
import Navbar from "../components/Navbar";
import toast from "react-hot-toast";
import { Save } from "lucide-react";

// no topo já tem imports
// ...

export default function PatientForm(){
  const [form,setForm]=useState<any>({name:"",cpf:"",height_m:"",weight_kg:"",allergies:"",meds_text:""});
  function upd(k:string,v:any){ setForm({...form,[k]:v}); }
  const onlyDigits = (s:string)=> s.replace(/\D+/g, "");

  async function save(e:any){ e.preventDefault();
    if(!form.name?.trim()){ toast.error("Informe o nome do paciente"); return; }
    const cpf = onlyDigits(form.cpf);
    if(cpf.length !== 11){ toast.error("CPF deve ter 11 dígitos"); return; }
    if(form.height_m && Number(form.height_m) <= 0){ toast.error("Altura inválida"); return; }
    if(form.weight_kg && Number(form.weight_kg) <= 0){ toast.error("Peso inválido"); return; }
    // payload
    const payload = {
      name: form.name.trim(),
      cpf,
      height_m: form.height_m ? parseFloat(form.height_m): null,
      weight_kg: form.weight_kg ? parseFloat(form.weight_kg): null,
      allergies: form.allergies ? form.allergies.split(",").map((s:string)=>s.trim()).filter(Boolean): [],
      meds: (form.meds_text? form.meds_text.split(",").map((s:string)=>({nome:s.trim()})): [])
    };
    try{
      const r = await api("/patients",{method:"POST", body: JSON.stringify(payload)});
      toast.success("Paciente salvo!");
      location.href = `/paciente/${r.id}`;
    }catch(err:any){
      console.error(err);
      toast.error("Falha ao salvar (veja o console).");
    }
  }

  return <>
    <Navbar />
    <div className="container">
      <div className="card">
        <div className="kicker">Cadastro</div>
        <h2 className="h2">Novo Paciente</h2>
        <form onSubmit={save} className="grid">
          <input placeholder="Nome completo *" onChange={e=>upd("name",e.target.value)} />
          <input placeholder="CPF (somente números) *" value={form.cpf} onChange={e=>upd("cpf", e.target.value)} />
          <div className="grid cols-2">
            <input placeholder="Altura (m)" onChange={e=>upd("height_m",e.target.value)} />
            <input placeholder="Peso (kg)" onChange={e=>upd("weight_kg",e.target.value)} />
          </div>
          <input placeholder="Alergias (separe por vírgula)" onChange={e=>upd("allergies",e.target.value)} />
          <input placeholder="Medicamentos (nome1, nome2...)" onChange={e=>upd("meds_text",e.target.value)} />
          <button className="btn"><Save size={16}/>Salvar</button>
        </form>
      </div>
    </div>
  </>;
}
