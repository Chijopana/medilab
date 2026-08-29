# 🚀 GUÍA RÁPIDA DE INICIO

## ⚡ Iniciar la Aplicación (30 segundos)

```bash
# 1. Abrir terminal en la carpeta del proyecto
cd "c:\Users\Jose\Documents\Cursos\IPIA\proyecto final\Proyecto_Final (1)\Proyecto_Final"

# 2. Activar entorno virtual
venv\Scripts\activate

# 3. Ejecutar servidor
python manage.py runserver

# 4. Abrir navegador
http://localhost:8000
```

---

## 🧪 Probar la Aplicación

### Opción A: Crear nuevo usuario (Recomendado)
1. Click en "Registrate"
2. Llenar el formulario:
   - Email: `test123@example.com`
   - DNI: `12345678A`
   - Contraseña: `MiPassword123!`
   - Confirmar contraseña: `MiPassword123!`
3. Click en "Crear Usuario"
4. Click en "Ir a Login"
5. Usar email/contraseña para entrar

### Opción B: Usar usuario de prueba (si existe)
```bash
# Verificar usuario en base de datos
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

---

## ✅ Verificación Rápida

Después de hacer login, verificar que funciona:

| Elemento | Estado |
|----------|--------|
| Menú "Medicación" | ✓ Sin errores |
| Menú "Visitas" | ✓ Sin errores |
| Menú "Historial Médico" | ✓ Sin errores |
| Menú "Perfil" | ✓ Sin errores |
| Estilos Bootstrap (colores, botones) | ✓ Visibles |
| CSS cargado | ✓ No hay 404s en consola |

---

## 🐛 Si Algo Falla

### Error 500 al hacer login
```bash
# Ver el error exacto
tail -f logs/medilab.log
```

### CSS no se ve (página con estilos rotos)
```bash
# Bootstrap debería estar aquí:
static/vendor/bootstrap/css/bootstrap.min.css
static/vendor/bootstrap/js/bootstrap.bundle.min.js

# Si no existen, ejecutar:
python setup_static_files.py
```

### Error: "Perfil has no pacientes"
```bash
# Ya está arreglado en este commit
# Si aún ves el error, ejecutar:
git pull  # O ver RESUMEN_FINAL_ARREGLOS.md
```

### ModuleNotFoundError: No module named 'django'
```bash
# Asegurarse de activar el entorno virtual
venv\Scripts\activate
```

---

## 📊 Estructura de Acceso

```
LOGIN:
  email: tu@email.com
  password: tuPassword

DESPUÉS DE LOGIN:
  ├── Medicación
  ├── Visitas
  ├── Historial Médico
  ├── Perfil
  ├── Detectar Enfermedad
  └── Logout
```

---

## 📁 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `manage.py` | Comando Django |
| `db.sqlite3` | Base de datos |
| `requirements.txt` | Dependencias Python |
| `venv/` | Entorno virtual |
| `static/` | CSS, JS, imágenes |
| `logs/` | Registros de aplicación |

---

## 🔧 Comandos Útiles

```bash
# Ver todos los usuarios registrados
python manage.py shell
>>> from django.contrib.auth.models import User
>>> for user in User.objects.all():
...     print(f"{user.username} - {user.email}")

# Ver si existen Pacientes
>>> from Perfiles.models import Paciente
>>> Paciente.objects.all()

# Ejecutar migraciones (si hay cambios en modelos)
python manage.py makemigrations
python manage.py migrate

# Ejecutar tests
python manage.py test

# Crear usuario desde terminal
python manage.py createsuperuser
```

---

## 📝 Qué Se Arregló

✅ Errores RelatedObjectDoesNotExist solucionados  
✅ Bootstrap CSS/JS descargados  
✅ Paciente se crea automáticamente al registrar  
✅ Todas las vistas de paciente y staff funcionan  

---

## 🎯 Próximos Pasos

Después de que funcione todo:

1. **Probar con múltiples usuarios**
2. **Revisar logs en `logs/audit.log`**
3. **Ejecutar tests: `python manage.py test`**
4. **Limpiar archivos duplicados** (ver `ANALISIS_ARCHIVOS.md`)
5. **Expandir funcionalidades**

---

**¡Listo para empezar!** 🚀

Ejecuta:
```bash
venv\Scripts\activate && python manage.py runserver
```

Abre: http://localhost:8000
