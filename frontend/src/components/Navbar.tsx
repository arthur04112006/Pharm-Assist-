import { Link } from "react-router-dom";
import { LogOut, FileDown, Plus } from "lucide-react";
import { api } from "../lib/api"; // usa nosso helper que já manda Authorization

export default function Navbar(){

  async function exportCSV(){
    try{
      const blob = await api("/export/patients.csv"); // GET com Authorization
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "pacientes.csv";
      a.click();
      URL.revokeObjectURL(url);
    }catch(e){
      console.error(e);
      alert("Falha ao exportar CSV (ver console).");
    }
  }

  return (
    <div className="navbar">
      <div className="wrap">
        <div className="brand">
          <span className="logo" />
          Pharm Assist
        </div>
        <span className="badge mono">MVP</span>
        <div className="spacer" />
        <button className="btn ghost" onClick={exportCSV}>
          <FileDown size={16}/> Exportar CSV
        </button>
        <Link to="/paciente/novo" className="btn"><Plus size={16}/> Novo Paciente</Link>
        <Link to="/" onClick={()=>localStorage.clear()} className="btn ghost"><LogOut size={16}/>Sair</Link>
      </div>
    </div>
  );
}
