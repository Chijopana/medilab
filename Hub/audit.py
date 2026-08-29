"""
Sistema de logging para auditoría de cambios en datos sensibles.
"""
import logging
from django.contrib.auth.models import User
from datetime import datetime
import json

# Configurar logger
logger = logging.getLogger(__name__)


class AuditLog:
    """Clase para registrar cambios en datos sensibles de la aplicación."""
    
    ACCIONES = {
        'LOGIN': 'Inicio de sesión',
        'LOGOUT': 'Cierre de sesión',
        'CREAR_USUARIO': 'Crear usuario',
        'CREAR_EXPEDIENTE': 'Crear expediente',
        'MODIFICAR_EXPEDIENTE': 'Modificar expediente',
        'ELIMINAR_EXPEDIENTE': 'Eliminar expediente',
        'VER_EXPEDIENTE': 'Ver expediente',
        'CREAR_MEDICACION': 'Crear medicación',
        'ELIMINAR_MEDICACION': 'Eliminar medicación',
        'ACCESO_DENEGADO': 'Acceso denegado',
    }
    
    @staticmethod
    def registrar_accion(usuario, accion, descripcion='', objeto_id=None):
        """
        Registra una acción en el log de auditoría.
        
        Args:
            usuario: Usuario que realiza la acción
            accion: Código de la acción (ver ACCIONES)
            descripcion: Descripción adicional de la acción
            objeto_id: ID del objeto afectado (expediente, medicación, etc)
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            nombre_accion = AuditLog.ACCIONES.get(accion, accion)
            
            # Obtener IP si está disponible
            ip = 'desconocida'
            
            # Crear mensaje de log
            log_message = (
                f"[{timestamp}] Usuario: {usuario.username} | "
                f"Acción: {nombre_accion} | "
                f"IP: {ip} | "
                f"Descripción: {descripcion}"
            )
            
            if objeto_id:
                log_message += f" | Objeto ID: {objeto_id}"
            
            # Registrar en el logger
            if accion == 'ACCESO_DENEGADO':
                logger.warning(log_message)
            else:
                logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Error al registrar auditoría: {str(e)}")
    
    @staticmethod
    def registrar_acceso_denegado(usuario, vista, razon=''):
        """Registra un intento de acceso denegado."""
        descripcion = f"Acceso denegado a: {vista}"
        if razon:
            descripcion += f" - Razón: {razon}"
        
        AuditLog.registrar_accion(
            usuario,
            'ACCESO_DENEGADO',
            descripcion
        )
    
    @staticmethod
    def registrar_cambio_expediente(usuario, expediente, accion, cambios_dict=None):
        """
        Registra cambios en un expediente.
        
        Args:
            usuario: Usuario que hace el cambio
            expediente: Objeto expediente
            accion: Crear/Modificar/Eliminar
            cambios_dict: Dict con los cambios realizados
        """
        descripcion = f"Expediente del paciente: {expediente.paciente.perfil.nombre}"
        
        if cambios_dict:
            cambios_json = json.dumps(cambios_dict, ensure_ascii=False)
            descripcion += f" - Cambios: {cambios_json}"
        
        AuditLog.registrar_accion(
            usuario,
            accion,
            descripcion,
            objeto_id=expediente.id
        )


class LoggerMiddleware:
    """Middleware para registrar acciones HTTP importantes."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rutas_auditadas = [
            '/Pacientes/',
            '/Staff/',
            '/expedientes/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Registrar si la ruta es auditada
        if any(request.path.startswith(ruta) for ruta in self.rutas_auditadas):
            if request.user.is_authenticated:
                if request.method in ['POST', 'PUT', 'DELETE']:
                    accion = f"{request.method} {request.path}"
                    AuditLog.registrar_accion(
                        request.user,
                        'OPERACION_HTTP',
                        f"Operación: {accion}"
                    )
        
        response = self.get_response(request)
        return response
