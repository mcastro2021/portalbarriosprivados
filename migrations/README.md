# Migraciones de Base de Datos

## Migración a PostgreSQL

### 1. Configuración de Alembic

```bash
# Inicializar Alembic
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migración
flask db upgrade
```

### 2. Migración desde SQLite a PostgreSQL

```python
# Script de migración
python migrate_to_postgresql.py
```

### 3. Comandos Útiles

```bash
# Ver historial de migraciones
flask db history

# Revertir última migración
flask db downgrade

# Ver estado actual
flask db current
```

## Estructura de Migraciones

- `versions/` - Archivos de migración
- `alembic.ini` - Configuración de Alembic
- `env.py` - Entorno de migración
- `script.py.mako` - Template para migraciones

## Mejoras Implementadas

1. **Índices para consultas frecuentes**
2. **Soft deletes**
3. **Constraints de integridad**
4. **Optimización de consultas**

## Notas Importantes

- Siempre hacer backup antes de migrar
- Probar migraciones en desarrollo primero
- Verificar integridad de datos después de migrar
