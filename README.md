# Medilab - Sistema de Gestión Médica
 
Aplicación Django para gestión de expedientes médicos, con diagnóstico asistido por IA (imagen → predicción real), chatbot y gestión de pacientes/staff.
 
## Estado actual
 
- ✅ Rediseño completo de interfaz: de landing tipo "web de hospital" a app de 3 accesos (Diagnóstico IA, Chatbot, Mis expedientes)
- ✅ Login y registro de pacientes funcionando (contraseña cifrada correctamente)
- ✅ Diagnóstico por IA con modelos reales descargados de Hugging Face:
  - **Neumonía** (radiografía de tórax) — funcional
  - **Lunares / melanoma** — funcional
  - **Tumor cerebral** (resonancia magnética) — funcional
  - **Tuberculosis** (radiografía de tórax) — ⚠️ **no funcional todavía**, se cuelga al procesar (en investigación, probablemente relacionado con el servidor de desarrollo de Django y no con el modelo en sí)
- ⚠️ Registro de médicos: no está conectado (el formulario apunta a un endpoint que no existe)
- ⚠️ "Historial" en el panel de paciente muestra datos de ejemplo fijos, no viene de la base de datos todavía
- ⏳ Vista de cuenta Staff/Médico: pendiente de probar a fondo
## Requisitos
 
- **Python 3.11** (no usar 3.12+ ni 3.14 — TensorFlow y varias dependencias no tienen wheels compatibles todavía en Windows)
- pip
## Instalación
 
### 1. Entorno virtual con Python 3.11
```powershell
py -3.11 -m venv venv
venv\Scripts\activate
```
 
### 2. Dependencias
```powershell
pip install -r requirements.txt
pip install huggingface_hub
```
 
### 3. Migraciones
```powershell
python manage.py migrate
```
 
### 4. Descargar los modelos de IA
No van incluidos en el repositorio por su tamaño. Créalos así:
```powershell
python manage.py shell
```
```python
import os, shutil
from huggingface_hub import hf_hub_download
 
os.makedirs('expedientes/modelos_ia', exist_ok=True)
 
p1 = hf_hub_download(repo_id="ayushirathour/chest-xray-pneumonia-detection", filename="best_chest_xray_model.h5")
shutil.copy(p1, 'expedientes/modelos_ia/pneumonia.h5')
 
p2 = hf_hub_download(repo_id="lizardwine/Melanoma-003", filename="Melanoma-003.keras")
shutil.copy(p2, 'expedientes/modelos_ia/lunares.keras')
 
p3 = hf_hub_download(repo_id="Owos/tb-classifier", filename="tb_model.h5")
shutil.copy(p3, 'expedientes/modelos_ia/tuberculosis.h5')
 
p4 = hf_hub_download(repo_id="larrikin-coder/brain-tumor-cnn", filename="cnn_model.h5")
shutil.copy(p4, 'expedientes/modelos_ia/tumor_cerebral.h5')
```
 
### 5. Crear superusuario y grupos
```powershell
python manage.py createsuperuser
```
Grupos necesarios (crear desde `/admin/` → Autenticación y Autorización → Grupos): `Pacientes`, `Medicos`
 
### 6. Arrancar
```powershell
python manage.py runserver
```
App en: **http://127.0.0.1:8000/**
 
## Estructura de carpetas
 
```
Proyecto_Final/
├── Proyecto_Final/       # settings.py, urls.py principales
├── Hub/                  # Landing, login, registro
├── Pacientes/            # Panel de paciente (perfil, historial, visitas, medicación)
├── Staff/                # Panel médico
├── Perfiles/             # Modelo Perfil/Paciente/Medico
├── Enfermedades/         # Modelos de diagnóstico (histórico)
├── expedientes/          # Expedientes + Diagnóstico con IA real
│   └── modelos_ia/       # Modelos .h5/.keras descargados (no en git)
├── chatbot/              # Chatbot de texto (intents)
├── static/css/app-theme.css   # Estilos de la nueva interfaz
└── db.sqlite3
```
 
## Diseño
 
La interfaz sigue una paleta propia (`static/css/app-theme.css`, variables `--teal`, `--teal-deep`, `--pulse`) aplicada sobre los componentes de Bootstrap ya usados en el proyecto — no se tocó `main.css` original salvo dejar de cargarlo (generaba conflictos con las pestañas de login/registro).
 
## Problemas conocidos
 
- Tuberculosis: la predicción se cuelga sin error visible. CPU no sube durante el cuelgue → probablemente conexión zombie del servidor de desarrollo, no el modelo. Pendiente de confirmar con servidor recién reiniciado y una sola pestaña de navegador.
- Registro de médicos no conectado a un grupo real.
- "Historial médico" del paciente es contenido de ejemplo fijo en el template.
## Seguridad en producción (antes de desplegar)
 
1. `DEBUG = False`
2. `SECRET_KEY` por variable de entorno
3. `ALLOWED_HOSTS` configurado
4. HTTPS/SSL
5. PostgreSQL en vez de SQLite
6. Backups de base de datos
7. Gunicorn + Nginx
 