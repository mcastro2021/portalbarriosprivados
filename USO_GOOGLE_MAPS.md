# Uso de Google Maps en el Proyecto

## Resumen
Google Maps se está utilizando en el proyecto para funcionalidades de geocodificación y servicios de ubicación. El módulo `googlemaps` de Python se usa principalmente en el backend para procesar direcciones y coordenadas.

## Ubicaciones de Uso

### 1. **Archivo Principal**: `external_integrations.py`

#### **Clase MapService** (líneas 515-615)
```python
# Inicialización del cliente Google Maps
google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if google_api_key:
    self.gmaps = googlemaps.Client(key=google_api_key)
```

#### **Funciones que usan Google Maps**:

**a) `geocode_address(address: str)`** (líneas 532-545)
- **Propósito**: Convertir direcciones en coordenadas (latitud/longitud)
- **Uso de Google Maps**: `self.gmaps.geocode(address)`
- **Fallback**: Si Google Maps no está disponible, usa Nominatim (Geopy)

**b) `reverse_geocode(latitude: float, longitude: float)`** (líneas 564-580)
- **Propósito**: Convertir coordenadas en direcciones
- **Uso de Google Maps**: `self.gmaps.reverse_geocode((latitude, longitude))`
- **Fallback**: Si Google Maps no está disponible, usa Nominatim (Geopy)

**c) `get_nearby_places(latitude, longitude, radius, type_)`** (líneas 615-625)
- **Propósito**: Obtener lugares cercanos a una ubicación
- **Uso de Google Maps**: `self.gmaps.places_nearby(location=(latitude, longitude), radius=radius, type=type_)`

### 2. **Archivo de Dependencias**: `optional_dependencies.py`

#### **Verificación de Disponibilidad** (línea 51)
```python
GOOGLEMAPS_AVAILABLE = safe_import('googlemaps') is not None
```

#### **Función de Importación** (líneas 81-83)
```python
def get_googlemaps():
    """Obtener googlemaps si está disponible"""
    return safe_import('googlemaps')
```

### 3. **Archivo de Instalación**: `install_dependencies.py`

#### **Dependencia Listada** (línea 40)
```python
"googlemaps==4.10.0",
```

### 4. **Archivo de Rutas**: `routes/external_routes.py`

#### **Verificación de Disponibilidad** (líneas 14, 98)
```python
GOOGLEMAPS_AVAILABLE, OPENWEATHERMAP_AVAILABLE, GEOPY_AVAILABLE,
```

#### **Endpoint de Geocodificación** (líneas 98-125)
- **Ruta**: `/location/geocode`
- **Método**: POST
- **Verificación**: `if not GOOGLEMAPS_AVAILABLE and not GEOPY_AVAILABLE:`
- **Uso**: Llama a `external_integrations.get_location_info(address=address)`

#### **Endpoint de Geocodificación Inversa** (líneas 127-155)
- **Ruta**: `/location/reverse-geocode`
- **Método**: POST
- **Uso**: Llama a `external_integrations.get_location_info(latitude=latitude, longitude=longitude)`

## Configuración Requerida

### **Variable de Entorno**
```bash
GOOGLE_MAPS_API_KEY=tu_api_key_de_google_maps
```

### **Dependencia Python**
```bash
pip install googlemaps==4.10.0
```

## Funcionalidades Implementadas

### 1. **Geocodificación de Direcciones**
- Convierte direcciones en coordenadas GPS
- Ejemplo: "Av. Corrientes 123, Buenos Aires" → lat/lng

### 2. **Geocodificación Inversa**
- Convierte coordenadas GPS en direcciones
- Ejemplo: lat/lng → "Av. Corrientes 123, Buenos Aires"

### 3. **Búsqueda de Lugares Cercanos**
- Encuentra lugares cercanos a una ubicación
- Configurable por radio y tipo de lugar

### 4. **Sistema de Fallback**
- Si Google Maps no está disponible, usa Nominatim (Geopy)
- Garantiza funcionalidad incluso sin API key

## Endpoints API Disponibles

### **POST /external/location/geocode**
```json
{
    "address": "Av. Corrientes 123, Buenos Aires"
}
```

### **POST /external/location/reverse-geocode**
```json
{
    "latitude": -34.6037,
    "longitude": -58.3816
}
```

## Estado de Implementación

### ✅ **Implementado**
- Cliente Google Maps inicializado
- Funciones de geocodificación
- Funciones de geocodificación inversa
- Búsqueda de lugares cercanos
- Sistema de fallback con Nominatim
- Endpoints API para geocodificación
- Verificación de disponibilidad

### ❌ **No Implementado**
- Integración en frontend (templates)
- Mapas interactivos con Google Maps JavaScript API
- Visualización de mapas en la interfaz web

## Notas Importantes

1. **API Key**: Requiere una API key válida de Google Maps
2. **Límites**: Google Maps tiene límites de uso y costos asociados
3. **Fallback**: El sistema funciona sin Google Maps usando Nominatim
4. **Frontend**: Los templates actuales usan mapas estáticos, no Google Maps

## Recomendaciones

1. **Para Producción**: Configurar API key de Google Maps para mejor precisión
2. **Para Desarrollo**: El sistema funciona sin API key usando Nominatim
3. **Costos**: Monitorear uso de la API de Google Maps para controlar costos
4. **Frontend**: Considerar integrar Google Maps JavaScript API para mapas interactivos
