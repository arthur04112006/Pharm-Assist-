import { useState } from "react";
import { api } from "../lib/api";

export default function Login(){
  const [email,setEmail]=useState(""); const [password,setPassword]=useState("");
  async function onSubmit(e:any){ e.preventDefault();
    const res = await api("/auth/login",{ method:"POST", body: JSON.stringify({email,password}) });
    localStorage.setItem("token", res.token); location.href="/dashboard";
  }
  return <div className="container">
    <div className="card"><h2>Login</h2>
      <form onSubmit={onSubmit}>
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
        <input placeholder="Senha" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
        <button className="btn" type="submit">Entrar</button>
      </form>
    </div>
  </div>;
}
