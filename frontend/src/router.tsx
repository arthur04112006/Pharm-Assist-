import { createBrowserRouter } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PatientForm from "./pages/PatientForm";
import PatientView from "./pages/PatientView";
import Questionnaire from "./pages/Questionnaire";
import Summary from "./pages/Summary";

export const router = createBrowserRouter([
  { path: "/", element: <Login/> },
  { path: "/dashboard", element: <Dashboard/> },
  { path: "/paciente/novo", element: <PatientForm/> },
  { path: "/paciente/:id", element: <PatientView/> },
  { path: "/atendimento/iniciar/:id", element: <Questionnaire/> },
  { path: "/atendimento/resumo/:id", element: <Summary/> }
]);
