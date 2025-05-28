⚠️Por favor leer notas al final⚠️
**Security Camera IA - Proyecto de Detección Inteligente**  
*(Proyecto Educativo - No Comercial)*  

---

### **Descripción General**  
Este sistema de vigilancia inteligente combina visión por computadora, IoT y cloud computing 
para demostrar las capacidades y limitaciones prácticas de la IA en seguridad. 
Desarrollado como proyecto de investigación académica, explora:  

- **Límites de la detección en tiempo real**  
- **Integración hardware/software**  
- **Escalabilidad de soluciones basadas en IA**  

---

### **Características Técnicas**  
| Componente | Tecnologías | Función |  
|------------|-------------|---------|  
| **Detección** | YOLOv8, OpenCV, Supervision | Identificación de personas con modelo pre-entrenado |  
| **Notificaciones** | SMTP, Gmail API | Alertas por email con capturas |  
| **Cloud** | Firebase (Storage, Firestore) | Almacenamiento y registro histórico |  
| **Hardware** | Arduino Serial | Activación de dispositivos físicos |  
| **Interfaz** | Tkinter | Panel de control básico |  

---

### **Flujo de Operación**  
1. **Detección en Tiempo Real**:  
   - Analiza flujo de video usando YOLOv8  
   - Define zonas de interés con polígonos virtuales  
   - Registra estadísticas de presencia humana  

2. **Respuesta Automatizada**:  
   - Envía señales a Arduino para actuadores físicos  
   - Notifica vía email tras 10 detecciones consecutivas  
   - Almacena evidencias en Firebase con timestamp  

3. **Integración Móvil**:  
   - App Android muestra histórico de alertas con imagenes de la persona detectada  
   - Acceso a imágenes clasificadas en la nube  

---

### **Limitaciones Reconocidas**  
- Interfaz gráfica básica (foco en funcionalidad sobre diseño)  
- Modelo pre-entrenado sin fine-tuning específico  
- Latencia en procesamiento de video HD  
- Dependencia de conexión estable a internet  

---

### **Equipo de Desarrollo**  
- **Liderazgo Técnico**: Vicente Scheihing (Arquitectura del Sistema y Construcción Aplicación Movil)  
- **Colaboradores**:  
  - Alexis Gallegos (Integración a Firebase)
  - Gonzalo Morales (Integración a Firebase)  
  - Daniel Uribe (Comunicación SMTP)  
  - Cristoffer Gatica (Comunicación SMTP) 
 

*Nota: Código compartido como referencia educativa - No apto para implementación productiva*

⚠️*Nota importante: Este proyecto no funciona porque las credenciales de Firebase fueron expuestas públicamente y deshabilitadas por seguridad. Usa tus propias credenciales de Firebase para probarlo localmente, ya que las claves de servicios nunca deben subirse a repositorios públicos.*⚠️
