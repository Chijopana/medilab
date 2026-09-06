"""
Auditoría de accesos y cambios sobre datos sensibles (historia clínica).

Todo lo que se registra aquí acaba en `logs/audit.log` (ver LOGGING en settings).
El middleware `AuditoriaMiddleware` deja rastro automático de las operaciones de
escritura sobre las rutas clínicas; para eventos concretos (ver un expediente,
denegar un acceso) se usa `AuditLog` directamente desde las vistas.
"""
import logging

logger = logging.getLogger(__name__)


class AuditLog:
    """Registro de acciones sobre datos sensibles de la aplicación."""

    ACCIONES = {
        'LOGIN': 'Inicio de sesión',
        'LOGIN_FALLIDO': 'Intento de inicio de sesión fallido',
        'LOGOUT': 'Cierre de sesión',
        'CREAR_USUARIO': 'Crear usuario',
        'CREAR_EXPEDIENTE': 'Crear expediente',
        'MODIFICAR_EXPEDIENTE': 'Modificar expediente',
        'ELIMINAR_EXPEDIENTE': 'Eliminar expediente',
        'VER_EXPEDIENTE': 'Ver expediente',
        'DESCARGAR_EXPEDIENTE': 'Descargar expediente en PDF',
        'DIAGNOSTICO_IA': 'Ejecutar diagnóstico por IA',
        'MODIFICAR_PACIENTE': 'Modificar datos de paciente',
        'CREAR_VISITA': 'Crear visita',
        'MODIFICAR_VISITA': 'Modificar visita',
        'ELIMINAR_VISITA': 'Eliminar visita',
        'CREAR_MEDICACION': 'Crear medicación',
        'ELIMINAR_MEDICACION': 'Eliminar medicación',
        'ACCESO_DENEGADO': 'Acceso denegado',
        'OPERACION_HTTP': 'Operación HTTP sobre datos clínicos',
    }

    @staticmethod
    def _ip(request):
        if request is None:
            return 'desconocida'
        reenviada = request.META.get('HTTP_X_FORWARDED_FOR')
        if reenviada:
            return reenviada.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'desconocida')

    @staticmethod
    def registrar(usuario, accion, descripcion='', objeto_id=None, request=None):
        """Escribe una línea en el log de auditoría.

        `usuario` puede ser un User o None (usuario anónimo).
        """
        try:
            nombre_usuario = getattr(usuario, 'username', None) or 'anónimo'
            nombre_accion = AuditLog.ACCIONES.get(accion, accion)

            partes = [
                f"Usuario: {nombre_usuario}",
                f"Acción: {nombre_accion}",
                f"IP: {AuditLog._ip(request)}",
            ]
            if descripcion:
                partes.append(f"Descripción: {descripcion}")
            if objeto_id is not None:
                partes.append(f"Objeto ID: {objeto_id}")

            mensaje = ' | '.join(partes)

            if accion in ('ACCESO_DENEGADO', 'LOGIN_FALLIDO'):
                logger.warning(mensaje)
            else:
                logger.info(mensaje)
        except Exception:
            # La auditoría nunca debe tumbar una petición.
            logger.exception('Error al registrar la auditoría')

    @staticmethod
    def acceso_denegado(usuario, vista, razon='', request=None):
        descripcion = f"Acceso denegado a: {vista}"
        if razon:
            descripcion += f" - Razón: {razon}"
        AuditLog.registrar(usuario, 'ACCESO_DENEGADO', descripcion, request=request)


class AuditoriaMiddleware:
    """Deja rastro de las escrituras sobre las rutas que manejan datos clínicos."""

    RUTAS_AUDITADAS = ('/Pacientes/', '/Staff/', '/expedientes/', '/admin/')
    METODOS_AUDITADOS = ('POST', 'PUT', 'PATCH', 'DELETE')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.method in self.METODOS_AUDITADOS
                and request.path.startswith(self.RUTAS_AUDITADAS)):
            usuario = getattr(request, 'user', None)
            if usuario is not None and usuario.is_authenticated:
                AuditLog.registrar(
                    usuario,
                    'OPERACION_HTTP',
                    f"{request.method} {request.path} -> {response.status_code}",
                    request=request,
                )
        return response
