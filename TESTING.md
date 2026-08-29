# Guía de Testing - Medilab

## Ejecutar los Tests

### Tests Básicos
```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de un módulo específico
python manage.py test tests

# Ejecutar un test específico
python manage.py test tests.RegistroUsuarioTest.test_registro_usuario_exitoso
```

### Tests con Verbose
```bash
# Ver detalles de cada test
python manage.py test --verbosity=2

# Ver más detalles
python manage.py test -v 3
```

### Coverage (Cobertura de Tests)
```bash
# Instalar coverage
pip install coverage

# Ejecutar tests con coverage
coverage run --source='.' manage.py test

# Ver reporte
coverage report

# Generar reporte HTML
coverage html
# Abrir: htmlcov/index.html
```

## Qué se Prueba

### 1. Registro de Usuarios
- ✓ Página de registro carga correctamente
- ✓ Registro exitoso de nuevos usuarios
- ✓ Validación de contraseñas que no coinciden
- ✓ Asignación correcta a grupos

### 2. Login
- ✓ Página de login carga correctamente
- ✓ Login exitoso de pacientes
- ✓ Login exitoso de médicos
- ✓ Redirección correcta según rol
- ✓ Rechazo de credenciales inválidas

### 3. Autorización
- ✓ Redireccionamiento a login sin autenticación
- ✓ Acceso a páginas protegidas con autenticación
- ✓ Rechazo de acceso sin rol adecuado

### 4. Logout
- ✓ Cierre de sesión exitoso
- ✓ Redirección a login después de logout

## Agregar Nuevos Tests

### Estructura de un Test
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from Perfiles.models import Perfil

class MisTests(TestCase):
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.client = Client()
        # Crear datos de prueba
    
    def test_mi_funcionalidad(self):
        """Probar una funcionalidad específica"""
        # Arrange - Preparar
        # Act - Ejecutar
        # Assert - Verificar
        self.assertEqual(1, 1)
    
    def tearDown(self):
        """Se ejecuta después de cada test"""
        # Limpiar datos
```

### Métodos de Aserción Comunes
```python
# Igualdad
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Verdadero/Falso
self.assertTrue(x)
self.assertFalse(x)

# Contenencia
self.assertIn(a, b)
self.assertNotIn(a, b)

# Responses HTTP
self.assertEqual(response.status_code, 200)
self.assertRedirects(response, url)
self.assertContains(response, text)
self.assertTemplateUsed(response, 'template.html')

# Formularios
self.assertFormError(response, 'form', 'field', 'error')

# Modelos
self.assertIsNotNone(objeto)
self.assertIsNone(objeto)
```

### Ejemplo: Test de Vista Protegida
```python
def test_vista_protegida_sin_login(self):
    """Verifica que una vista protegida requiere login"""
    response = self.client.get(reverse('pacientes/pagina_principal'))
    
    # Debe redirigir a login
    self.assertEqual(response.status_code, 302)
    self.assertIn(reverse('log_in'), response.url)

def test_vista_protegida_con_login(self):
    """Verifica que una vista protegida es accesible con login"""
    self.client.login(username='paciente1', password='Test123!')
    
    response = self.client.get(reverse('pacientes/pagina_principal'))
    
    # Debe cargar correctamente
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'pacientes/pagina_principal.html')
```

## Test Fixtures (Datos de Prueba)

### Crear un Fixture
```bash
# Exportar datos de la BD
python manage.py dumpdata app.Model > fixtures/datos.json

# Usar en tests
class MisTests(TestCase):
    fixtures = ['datos.json']
```

## Pruebas de Rendimiento

```bash
# Medir tiempo de test
python manage.py test --timing

# Con Django Debug Toolbar
pip install django-debug-toolbar
```

## Integración Continua (CI)

### Configurar GitHub Actions
Crear archivo: `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: test_medilab
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
      env:
        DATABASE_URL: postgresql://test:test@localhost/test_medilab
```

## Debugging de Tests

```python
# En el test, usar breakpoint
def test_mi_test(self):
    resultado = mi_funcion()
    breakpoint()  # Pausa la ejecución
    self.assertEqual(resultado, esperado)

# Ejecutar con debugger
python -m pdb manage.py test
```

## Próximos Pasos

1. **Aumentar cobertura**: Objetivo mínimo 80%
2. **Tests de integración**: Probar flujos completos
3. **Tests de carga**: Usar locust o similar
4. **Pruebas manuales**: Casos de uso reales
