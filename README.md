# Medilab — Sistema de gestión médica

Aplicación Django para la gestión de expedientes médicos, con diagnóstico asistido
por IA sobre imagen, chatbot de intenciones y paneles separados para pacientes y
personal sanitario.

---

## Puesta en marcha

### 1. Entorno virtual (Python 3.11)

TensorFlow no publica wheels para Windows en Python 3.12+, así que **hay que usar 3.11**.

```powershell
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuración

En desarrollo no necesitas hacer nada: si no existe `.env` y `DEBUG=True`, se genera
una `SECRET_KEY` temporal al arrancar. Para fijarla (o para producción):

```powershell
copy .env.example .env
```

### 3. Base de datos y datos de arranque

```powershell
python manage.py migrate
python manage.py init_datos --demo
```

`init_datos` crea los grupos `Pacientes`, `Medicos` y `Staff`. Con `--demo` añade
además dos médicos, cuatro pacientes y sus visitas, expedientes y medicación, para
poder enseñar la aplicación sin picar datos a mano.

| Rol      | Usuarios                   | Contraseña      |
|----------|----------------------------|-----------------|
| Médico   | `dra.ruiz`, `dr.navarro`   | `Medilab2026!`  |
| Paciente | `lucia`, `omar`, `irene`, `pau` | `Medilab2026!` |

Para el panel `/admin/`:

```powershell
python manage.py createsuperuser
```

### 4. Modelos de IA (opcional)

Pesan ~284 MB y no están en el repositorio. Sin ellos la aplicación funciona: la
pantalla de diagnóstico avisa de que el modelo no está instalado.

```powershell
pip install huggingface_hub
python manage.py shell
```

```python
import os, shutil
from huggingface_hub import hf_hub_download

os.makedirs('expedientes/modelos_ia', exist_ok=True)

for repo, fichero, destino in [
    ("ayushirathour/chest-xray-pneumonia-detection", "best_chest_xray_model.h5", "pneumonia.h5"),
    ("lizardwine/Melanoma-003",                      "Melanoma-003.keras",       "lunares.keras"),
    ("Owos/tb-classifier",                           "tb_model.h5",              "tuberculosis.h5"),
    ("larrikin-coder/brain-tumor-cnn",               "cnn_model.h5",             "tumor_cerebral.h5"),
]:
    shutil.copy(hf_hub_download(repo_id=repo, filename=fichero),
                f'expedientes/modelos_ia/{destino}')
```

Después, deja los modelos listos (convierte el de tuberculosis y comprueba el resto):

```powershell
python manage.py preparar_modelos_ia --probar
```

### 5. Arrancar

```powershell
python manage.py runserver
```

La aplicación queda en **http://127.0.0.1:8000/**

---

## Chatbot

El asistente responde sobre la propia aplicación: cómo pedir cita, dónde está el
historial, cómo descargar un expediente, qué hace el diagnóstico por IA, quién
puede ver tus datos... Ante síntomas o dudas de medicación deriva a un
profesional, y ante una urgencia remite al 112. Nunca diagnostica.

> El modelo que traía el proyecto estaba entrenado en **historia del arte** (48
> de sus 53 intenciones eran movimientos artísticos, de ahí que se llamara
> "Arte"). Contestaba sobre el Renacimiento a quien preguntaba por sus citas.

Todo el conocimiento vive en `chatbot/modelo/intents.json`. Para añadir o
cambiar respuestas, edita ese fichero y reentrena:

```powershell
python manage.py entrenar_chatbot
```

Cada intención tiene `patterns` (formas de preguntar, que son los ejemplos de
entrenamiento) y `responses` (de las que se elige una al azar). Si una pregunta
no supera el umbral de confianza, el bot admite que no la ha entendido en vez de
inventarse una respuesta.

---

## Estructura

```
Proyecto_Final/
├── Proyecto_Final/     settings.py y urls.py del proyecto
├── Hub/                portada, login, registro, auditoría, decoradores y reglas de acceso
│   ├── accesos.py      "¿puede esta persona ver esto?" — centralizado
│   ├── audit.py        registro de auditoría + middleware
│   ├── decorators.py   @paciente_requerido, @medico_requerido, @staff_requerido
│   └── management/     comando init_datos
├── Perfiles/           Perfil, Paciente, Medico
├── Pacientes/          área del paciente y modelo Visita
├── Staff/              panel médico y modelo Medicacion
├── expedientes/        historia clínica, PDF y diagnóstico por IA
│   └── carga_modelos.py  carga y conversión de los modelos de Keras
├── Enfermedades/       datos clínicos por patología
├── chatbot/            asistente de intenciones (Keras)
│   └── modelo/intents.json  lo que el chatbot sabe responder
├── E404/               páginas de error 403/404/500
└── static/             Bootstrap, iconos e imágenes
```

---

## Seguridad

El proyecto maneja datos de salud, así que el acceso está cerrado por defecto:

- **Ninguna vista clínica es pública.** Todas llevan `@login_required` o uno de los
  decoradores de rol.
- **Aislamiento por paciente.** Un paciente solo alcanza sus propios datos: las
  consultas parten de `request.paciente`, nunca de un id de la URL.
- **Relación asistencial.** Un médico solo ve la ficha de los pacientes que atiende
  (`Medico.atiende()`). Conocer el `access_key` de otro paciente no sirve de nada.
- **404 en vez de 403** cuando no hay permiso, para no confirmar que ese recurso existe.
- **Auditoría** de accesos y escrituras sobre datos clínicos en `logs/audit.log`.
- **Secretos fuera del código**: `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` vienen del
  entorno. Con `DEBUG=False` y sin `SECRET_KEY`, el proyecto se niega a arrancar.
- **Cabeceras y cookies** endurecidas automáticamente al poner `DEBUG=False`
  (HSTS, redirección a HTTPS, cookies `Secure`, `X-Frame-Options: DENY`).
- Cerrar sesión exige **POST**, para que un enlace externo no pueda desloguearte.

Antes de desplegar, comprueba la configuración con:

```powershell
python manage.py check --deploy
```

Falta por hacer para un despliegue real: PostgreSQL en lugar de SQLite, servir con
Gunicorn/Nginx, HTTPS y copias de seguridad de la base de datos.

---

## Tests

```powershell
python manage.py test
```

Cubren registro, login/logout, aislamiento entre pacientes, relación asistencial en
el panel médico y el acceso a expedientes y a su PDF. Ver [TESTING.md](TESTING.md).

---

## Diseño

Interfaz propia sobre Bootstrap 5, definida en `Hub/static/css/app-theme.css`
(variables `--teal`, `--teal-deep`, `--pulse`). Cada rol tiene un layout de panel con
menú lateral: `pacientes/base_panel.html` y `staff/base_panel.html`.

La navegación son páginas reales, no fragmentos htmx: así las URLs se pueden
compartir, el botón "atrás" funciona y ninguna vista devuelve un trozo de HTML sin
estilos si se entra por la URL directa.

---

## Estado actual

**Funciona:**

- Registro y login de pacientes, con validación de contraseña de Django.
- Área del paciente: resumen, historial, visitas (crear, modificar, cancelar),
  medicación y datos personales.
- Panel médico: resumen, listado de pacientes con búsqueda y paginación, ficha del
  paciente, visitas, prescripción de medicación y perfil.
- Expedientes: consulta, vista imprimible y descarga en PDF.
- Diagnóstico por IA: **los cuatro modelos** — neumonía, tuberculosis,
  lunares/melanoma y tumor cerebral.
- Chatbot que responde sobre la aplicación.

**Limitaciones conocidas:**

- **El chatbot es un clasificador de intenciones**, no un modelo de lenguaje:
  responde bien a lo que está en `intents.json` y admite que no entiende el
  resto. Para que cubra algo nuevo hay que añadirlo y reentrenar.
- Los modelos de IA son de terceros y se entrenaron con conjuntos públicos: los
  resultados son orientativos y no están validados clínicamente.
- **Alta de médicos**: se hace desde `/admin/` o con `init_datos`. No hay
  autoregistro de personal sanitario, y es deliberado: cualquiera podría darse de
  alta como médico y acceder a datos de pacientes.
- **Bandeja de borradores** (`TemporalExpediente`): se listan, pero todavía no hay
  flujo para convertir un borrador en expediente firmado.
- La asignación de pacientes a un médico se hace desde `/admin/`.
- La primera vez que se usa tuberculosis, el modelo se convierte a formato
  `.keras` (unos 2 s). `preparar_modelos_ia` lo hace por adelantado.
