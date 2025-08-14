# 🤖 Asistente Virtual con Redirección Automática

## ✨ **Características Principales**

### 🚀 **Redirección Automática Inteligente**
El chatbot detecta automáticamente la intención del usuario y lo redirige a la sección correspondiente **sin necesidad de hacer clic en nada**.

### 🎯 **Palabras Clave Mágicas**
Usa estas palabras para activar la redirección automática:
- `ir a`, `llevar a`, `mostrar`, `ver`, `abrir`, `acceder`
- `crear`, `registrar`, `nuevo`, `nueva`, `agregar`
- `hacer`, `programar`, `agendar`, `reservar`, `pagar`

## 📋 **Ejemplos de Uso**

### **Visitas**
- ✅ `"Quiero registrar una nueva visita"` → Redirección automática a Nueva Visita
- ✅ `"Ver mis visitas"` → Redirección automática a Gestión de Visitas
- ✅ `"¿Tengo visitas pendientes?"` → Información + opción de redirección

### **Reservas**
- ✅ `"Hacer una reserva del quincho"` → Redirección automática a Nueva Reserva
- ✅ `"Ver calendario de reservas"` → Redirección automática a Calendario
- ✅ `"Mostrar mis reservas"` → Redirección automática a Gestión de Reservas

### **Expensas**
- ✅ `"Pagar mis expensas"` → Redirección automática a Expensas
- ✅ `"Ver estado de expensas"` → Redirección automática a Estado de Expensas

### **Mantenimiento**
- ✅ `"Crear un reclamo"` → Redirección automática a Nuevo Reclamo
- ✅ `"Ver mis reclamos"` → Redirección automática a Gestión de Mantenimiento

### **Navegación General**
- ✅ `"Ir al mapa"` → Redirección automática al Mapa Interactivo
- ✅ `"Ver mi perfil"` → Redirección automática al Perfil
- ✅ `"Mostrar noticias"` → Redirección automática a Noticias
- ✅ `"Panel de administración"` → Redirección automática al Admin (solo admin)

## 🎨 **Interfaz Inteligente**

### **Modal de Redirección**
- Cuenta regresiva de 3 segundos
- Botón "Ir Ahora" para redirección inmediata
- Botón "Cancelar" para quedarse en el chat
- Animaciones suaves y profesionales

### **Botón Flotante**
- Visible en todas las páginas
- Animación de pulso continua
- Tooltip informativo con hover
- Responsivo para móviles

### **Chat Inteligente**
- Detección automática de intenciones
- Respuestas contextuales
- Historial de conversación
- Botones de acción rápida
- Animaciones de escritura realistas

## 🛠️ **Tecnología**

### **Backend (Python/Flask)**
- Análisis inteligente de consultas
- Sistema de detección de intenciones
- Integración con OpenAI (opcional)
- Gestión de sesiones de chat
- APIs RESTful para comunicación

### **Frontend (JavaScript/Bootstrap)**
- Interfaz moderna y responsiva
- Animaciones CSS3 avanzadas
- Modal de redirección automática
- Chat en tiempo real
- Soporte para dispositivos móviles

## 🎯 **Casos de Uso Específicos**

### **Administradores**
- `"Crear nueva noticia"` → Nueva Noticia
- `"Administrar usuarios"` → Panel de Admin
- `"Ver reportes"` → Reportes de Admin

### **Residentes**
- `"¿Cuándo vence mi expensa?"` → Consulta + redirección opcional
- `"Registrar un invitado"` → Nueva Visita
- `"Reservar la cancha"` → Nueva Reserva

### **Consultas Múltiples**
- El bot maneja consultas complejas detectando la acción principal
- Prioriza acciones específicas sobre consultas generales
- Ofrece alternativas cuando hay ambigüedad

## 🚀 **Flujo de Redirección**

1. **Usuario escribe consulta** → `"Quiero hacer una reserva"`
2. **Bot analiza intención** → Detecta palabras clave `"hacer"` + `"reserva"`
3. **Bot responde** → `"Te estoy llevando a hacer una nueva reserva..."`
4. **Modal aparece** → Muestra destino y cuenta regresiva
5. **Redirección automática** → Lleva a `/reservations/new` en 2-3 segundos
6. **Usuario llega al destino** → Listo para usar la funcionalidad

## ⭐ **Beneficios**

- **Eficiencia**: Sin clics manuales, redirección automática
- **Intuitividad**: Lenguaje natural, sin comandos complejos
- **Ahorro de tiempo**: Acceso directo a funcionalidades
- **Experiencia moderna**: Interfaz tipo asistente virtual
- **Accesibilidad**: Disponible desde cualquier página
- **Inteligencia**: Entiende contexto y intenciones

¡El asistente virtual transforma la navegación del portal en una experiencia conversacional inteligente! 🎉
