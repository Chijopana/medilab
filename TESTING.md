# Tests

## Ejecutar

```powershell
python manage.py test                  # toda la suite (53 tests)
python manage.py test Hub              # solo una app
python manage.py test expedientes.tests.AccesoExpedienteTest
python manage.py test -v 2             # con detalle de cada test
```

Cobertura:

```powershell
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html          # informe navegable en htmlcov/index.html
```

---

## Qué se prueba

La suite está escrita alrededor de una idea: **que nadie pueda leer la historia
clínica de otra persona**. Cada bloque es una regresión de un fallo real que tenía
el proyecto.

### `Hub/tests.py` — registro y sesión

- La página de registro carga y el alta crea User + Perfil + Paciente + grupo.
- La contraseña se guarda cifrada, nunca en claro.
- Se rechazan: contraseñas que no coinciden, contraseñas débiles y DNI duplicado.
- Si el perfil no valida, **no queda un User huérfano** (el alta va en una transacción).
- Login: paciente y médico aterrizan cada uno en su panel; credenciales malas no entran.
- Un `?next=` que apunte fuera del sitio se ignora (open redirect).
- Cerrar sesión exige POST; un GET devuelve 405.

### `Pacientes/tests.py` — aislamiento entre pacientes

- Sin sesión, el área de paciente redirige al login.
- Un usuario sin rol, o un médico, no entran en el área de paciente.
- Un paciente **no ve, no abre y no borra** la visita de otro paciente.
- Borrar una visita exige POST.

### `Staff/tests.py` — rol y relación asistencial

- Un paciente no entra en el panel médico.
- Un médico ve la ficha de **sus** pacientes.
- Otro médico recibe 404 en ficha, edición, visitas, expedientes y medicación:
  conocer el `access_key` no basta.
- Un médico ajeno no puede editar los datos del paciente ni prescribirle nada.

### `expedientes/tests.py` — historia clínica

Aquí estaba el agujero más grave: `/expedientes/<id>/` y su PDF eran públicos y se
podía leer la historia de cualquiera probando números.

- Un anónimo no accede ni al expediente ni al PDF.
- El paciente lee el suyo; otro paciente recibe 404.
- El médico que le atiende lo lee; otro médico recibe 404.
- El PDF se genera de verdad (empieza por `%PDF`).
- El listado de expedientes solo muestra los propios.
- Diagnóstico por IA: exige login, una especialidad inventada ya no provoca un 500,
  y un fichero que no es una imagen se rechaza.

### `chatbot/tests.py` — el asistente

El modelo original venía entrenado en historia del arte, así que respondía sobre
el Renacimiento a quien preguntaba por sus citas.

- `intents.json` está bien formado: toda intención tiene frases y respuestas, y
  no hay etiquetas repetidas.
- Existen las intenciones propias de la aplicación (citas, historial, medicación,
  diagnóstico por IA, privacidad, urgencias).
- Ante síntomas o dudas de medicación, las respuestas derivan a un profesional;
  la intención de urgencia menciona el 112.
- Contrato HTTP: un GET devuelve 405, un mensaje vacío responde igualmente y uno
  de más de 500 caracteres se rechaza con 400.
- De punta a punta: preguntar «como pido una cita» devuelve la respuesta correcta
  del modelo entrenado.

### `expedientes/tests.py` — configuración de los modelos de IA

Regresión del cuelgue de tuberculosis:

- Cada modelo del catálogo declara `tamano` y `escalado`.
- Tuberculosis usa 300×300 y píxeles crudos (lleva `Rescaling(1/255)` dentro).
- El preprocesado respeta ambos: con `crudo` no divide entre 255, con `0-1` sí.

---

## Notas

- Los tests usan una base de datos temporal; no tocan `db.sqlite3`.
- Durante los tests la auditoría no escribe en consola (`EJECUTANDO_TESTS` en
  `settings.py`), para que la salida sea legible.
- `Hub/tests.py` expone `crear_paciente()` y `crear_medico()`; las demás apps los
  reutilizan en lugar de repetir el montaje.
- No hacen falta los modelos de IA para pasar la suite: los tests de IA
  comprueban la configuración y el preprocesado, no ejecutan las redes.
- El test de punta a punta del chatbot sí carga TensorFlow, y por eso la
  suite tarda algo más de un minuto.
