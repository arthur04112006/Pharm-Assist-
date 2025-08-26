const BASE = import.meta.env.VITE_API || "http://localhost:5000";
export function token(){ return localStorage.getItem("token") || ""; }
export async function api(path:string, opts:RequestInit = {}){
  const headers = new Headers(opts.headers);
  headers.set("Content-Type","application/json");
  if(token()) headers.set("Authorization",`Bearer ${token()}`);
  const res = await fetch(`${BASE}${path}`, {...opts, headers});
  if(!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.blob();
}
