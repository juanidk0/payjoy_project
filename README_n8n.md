# Flujo de n8n - PayJoy Customer Feedback Automation

Este proyecto implementa un sistema automatizado de procesamiento de feedback de clientes para PayJoy usando n8n. El workflow captura encuestas de satisfacción de múltiples tiendas, las procesa usando IA, y genera reportes automáticos tanto inmediatos como semanales.

## 🚀 Características principales

- **Captura automática** de encuestas desde Google Sheets de 3 tiendas
- **Procesamiento inteligente** con GPT-5 para análisis de sentimientos y categorización
- **Alertas inmediatas** para reviews negativas (experiencia < 4)
- **Reportes semanales** automatizados con métricas y insights
- **Almacenamiento** en base de datos PostgreSQL
- **Dashboard interactivo** con Streamlit para visualización de datos

## 📊 Arquitectura del Workflow

### Triggers principales:
1. **Google Sheets Triggers** (3 tiendas)
   - Monitorea nuevas filas en las hojas de cálculo de cada tienda
   - Ejecuta cada minuto para capturar respuestas en tiempo real

2. **Schedule Trigger**
   - Ejecuta semanalmente (lunes 6:00 AM) para generar reportes

### Procesamiento de datos:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO PRINCIPAL DE DATOS                      │
└─────────────────────────────────────────────────────────────────┘

Google Sheets (Tienda 1/2/3) 
         ↓
Procesar y estandarizar las rows
         ↓
Creador de dataset (IA - GPT-5)
         ↓
    ¿Experiencia < 4?
    ├─ SÍ → Alerta Email Inmediata
    └─ NO → Continúa
         ↓
Guardar en PostgreSQL
         ↓
Consolidado en Google Sheets

┌─────────────────────────────────────────────────────────────────┐
│                   FLUJO REPORTE SEMANAL                         │
└─────────────────────────────────────────────────────────────────┘

Schedule Trigger (Semanal)
         ↓
Obtener raw data resumen semanal
         ↓
Crear resumen semanal (IA)
         ↓
Enviar reporte semanal por email
```

## 🗃️ Estructura de datos

### Tabla PostgreSQL `reviews`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | SERIAL | ID único auto-incrementable |
| `tienda` | INT | Número de tienda (1, 2, 3) |
| `comentario_original` | TEXT | Comentario del cliente limpio |
| `experiencia` | INT | Calificación 1-5 |
| `sentimiento` | TEXT | Positivo/Neutral/Negativo |
| `categoria_principal` | TEXT | Categoría principal del feedback |
| `categoria_2` | TEXT | Categoría secundaria (opcional) |
| `categoria_3` | TEXT | Categoría terciaria (opcional) |
| `menciona_staff` | BOOLEAN | Si menciona al personal |
| `sugerencias` | TEXT | Sugerencias adicionales |
| `contacto` | TEXT | Información de contacto |
| `fecha` | TIMESTAMP | Fecha y hora del feedback |
| `resuelto` | BOOLEAN | Estado de seguimiento |

### Categorías de análisis automático:
1. **Atención al cliente / Trato al personal**
2. **Tiempo de espera / Filas**
3. **Disponibilidad de productos / Stock**
4. **Precios / Promociones**
5. **Calidad del producto**
6. **Proceso de pago / Financiamiento**
7. **Ambiente / Limpieza / Orden de la tienda**
8. **Soporte / Resolución de problemas**
9. **Sugerencias de mejoras generales**
10. **Spam**

## ⚙️ Configuración necesaria

### 1. Credenciales de n8n:
- **Google Sheets Trigger OAuth2 API**: Para acceso a las hojas de cálculo
- **OpenAI API**: Para procesamiento con GPT-5-NANO
- **PostgreSQL**: Base de datos para almacenamiento
- **SMTP**: Para envío de emails


## 📧 Sistema de notificaciones

### 🚨 Alertas inmediatas:
- **Trigger**: Reviews con experiencia < 4 estrellas
- **Destinario**: `juanpython2@gmail.com`
- **Contenido**: 
  - Detalles completos del feedback negativo
  - Información de la tienda
  - Sugerencias del cliente
  - Datos de contacto para seguimiento

### 📊 Reportes semanales:
- **Frecuencia**: Domingos a las 6:00 AM (Colombia)
- **Período**: Últimos 7 días
- **Contenido**: 
  - Total de reviews por tienda
  - Promedio de experiencia general
  - Distribución de sentimientos
  - Principales categorías mencionadas
  - Reviews que mencionan al staff
  - Insights y recomendaciones generadas por IA
  - Patrones identificados en los comentarios

## 🔧 Importación del workflow en n8n

### Paso 1: Importar el workflow
1. Abre n8n en tu navegador
2. Ve a **Workflows** → **Import from file**
3. Sube el archivo `prueba_PayJoy.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar credenciales
Necesitarás configurar las siguientes credenciales:

#### Google Sheets OAuth2:
- Crear proyecto en Google Cloud Console
- Habilitar Google Sheets API
- Crear credenciales OAuth2
- Configurar en n8n con los tokens

#### OpenAI API:
- Obtener API key de OpenAI
- Configurar en n8n con el modelo GPT-5-NANO-2025-08-07

#### PostgreSQL:
- Host, puerto, base de datos, usuario y contraseña
- Asegurar que la tabla `reviews` existe

#### SMTP (Gmail):
- Email: `juanpython2@gmail.com`
- Configurar app password de Gmail
- Puerto 587 con TLS

### Paso 3: Activar el workflow
1. Hacer clic en el botón **Active** en la esquina superior derecha
2. Verificar que todos los triggers están funcionando

## 🎯 Nodos principales del workflow

### Triggers:
- **Tienda 1 Trigger**: Monitorea Google Sheet de tienda 1
- **Tienda 2 Trigger**: Monitorea Google Sheet de tienda 2  
- **Tienda 3 Trigger**: Monitorea Google Sheet de tienda 3
- **Schedule Trigger**: Ejecuta reportes semanales

### Procesamiento:
- **Procesar y estandarizar las rows**: Limpia y normaliza datos
- **Creador de dataset**: Usa IA para análisis de sentimientos y categorización
- **If**: Evalúa si la experiencia es negativa (< 4)

### Salidas:
- **Insert rows in a table**: Guarda en PostgreSQL
- **Bad reviews report**: Envía alertas inmediatas
- **weekly report**: Envía reporte semanal
- **Consolidado**: Guarda en Google Sheets

### Utilidades:
- **Obtener raw data resumen semanal**: Filtra datos de la última semana
- **Crear resumen semanal**: Genera reporte con IA

## 📝 Mantenimiento y monitoreo

### Tareas regulares:
- **Verificar ejecuciones**: Revisar logs en n8n dashboard
- **Monitorear API usage**: Controlar uso de OpenAI API
- **Backup de datos**: Respaldar base de datos PostgreSQL
- **Validar emails**: Confirmar entrega de reportes

### Troubleshooting común:
- **Conexión a Google Sheets**: Verificar permisos OAuth2
- **Errores de IA**: Revisar prompts y límites de API
- **Base de datos**: Verificar conexión y espacio disponible
- **Emails no enviados**: Revisar configuración SMTP

### Personalización:
- **Horarios**: Modificar schedule trigger para diferentes horarios
- **Categorías**: Ajustar prompts de IA para nuevas categorías
- **Nuevas tiendas**: Duplicar triggers existentes
- **Templates de email**: Customizar formato de reportes

## 📊 Integración con Dashboard

Este workflow alimenta el dashboard de Streamlit (`dashboard_demo.py`) que se conecta a la misma base de datos PostgreSQL para:

- Visualizar métricas en tiempo real
- Filtrar y analizar datos históricos
- Gestionar casos pendientes
- Exportar reportes personalizados

El dashboard se ejecuta independientemente del workflow de n8n, pero utiliza los datos procesados por él.

## 🔐 Consideraciones de seguridad

- **Credenciales**: Todas las credenciales se almacenan de forma segura en n8n
- **Datos sensibles**: Los comentarios se limpian de caracteres especiales
- **Acceso**: Limitar acceso al workflow solo a usuarios autorizados
- **Logs**: Revisar logs regularmente para detectar anomalías
- **Backup**: Mantener respaldos de configuración del workflow

## 📈 Métricas y KPIs

El sistema permite monitorear:
- **Volumen de feedback** por tienda y período
- **Distribución de satisfacción** (1-5 estrellas)
- **Sentimientos** (Positivo/Neutral/Negativo)
- **Tiempo de respuesta** a feedback negativo
- **Categorías más mencionadas** por los clientes
- **Tendencias** de satisfacción en el tiempo

---

*Para más información sobre el dashboard de visualización, consulta el archivo `README.md` principal.*