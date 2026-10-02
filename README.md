# BackendFASTAPI
## Resumen
Backend de agenda desarrollado con FastAPI, SQLModel y SQLite. Incluye una API con autenticación JWT y una interfaz web Jinja2 para registrar usuarios, iniciar sesión y administrar contactos propios.

## Vistas web

/views/register: crea una cuenta y, si el registro es válido, inicia sesión automáticamente.
/views/login: valida usuario y contraseña.
/views/agenda: requiere sesión y muestra únicamente los contactos del usuario autenticado.
/views/logout: cierra la sesión y elimina la cookie.
El JWT se conserva en una cookie HttpOnly durante 60 minutos. La creación de contactos desde la agenda asigna automáticamente su propietario; ya no se puede elegir otra cuenta escribiendo su nombre de usuario.

## API

POST /auth/register: registro vía API.
POST /auth/token: obtiene un JWT para clientes API y Swagger.
/agenda: CRUD protegido. Las operaciones comprueban que el contacto pertenezca al usuario autenticado.
/docs: documentación interactiva de Swagger.
Persistencia
Los registros se guardan en agenda.db. Detener la aplicación no borra usuarios ni contactos. El inicio crea las tablas que falten, pero no migra cambios de esquema en tablas existentes.

## Validación reciente

Registro, login web y cookie HttpOnly: correctos.
Contactos aislados entre dos usuarios: correcto.
Cierre de sesión y bloqueo posterior de la agenda: correctos.
Swagger y página de login respondieron 200.
Compilación del proyecto correcta y una sola instancia escuchando en el puerto 8000.
Se eliminaron los datos temporales usados durante las pruebas.
Pendientes y límites

No hay recuperación de contraseña; la contraseña original no se puede leer porque se guarda con bcrypt.
SECRET_KEY aún tiene un valor de ejemplo predeterminado; debe configurarse mediante una variable de entorno antes de producción.
CORS permite cualquier origen y conviene limitarlo a los dominios necesarios.
VS Code/Pylance no está resolviendo las dependencias Python aunque la app compila y funciona con fastAPIenv; selecciona ese entorno como intérprete del proyecto.
