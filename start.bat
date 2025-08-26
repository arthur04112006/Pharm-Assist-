@echo off
title Pharm Assist - Inicializador

echo === Iniciando Backend ===
cd backend
start cmd /k ".venv\Scripts\python.exe app.py"
cd ..

echo === Iniciando Frontend ===
cd frontend
start cmd /k "npm run dev"
cd ..

echo.
echo ✅ Projeto iniciado! 
echo Abra http://localhost:5173 no navegador.
pause
