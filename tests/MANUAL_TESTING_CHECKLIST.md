# ✅ Checklist de Testing Manual - Tag Groups & Smart Collections

**Versión:** 1.0
**Fecha:** 2025-11-05
**Sistema:** Widget Sidebar v3.1

---

## 📋 Instrucciones de Uso

1. Ejecuta cada test en orden
2. Marca ✅ cuando pase, ❌ cuando falle
3. Anota cualquier bug o comportamiento inesperado en la sección de notas
4. Si un test falla, intenta reproducirlo 2-3 veces antes de reportar
5. Toma screenshots de bugs cuando sea posible

---

## 🧪 SECCIÓN 1: Tag Groups Manager

### 1.1 Acceso al Manager

- [ ] **Test 1.1.1:** Abrir Settings → General
- [ ] **Test 1.1.2:** Verificar que existe sección "🏷️ Grupos de Tags"
- [ ] **Test 1.1.3:** Click en "📋 Gestionar Grupos de Tags"
- [ ] **Test 1.1.4:** Verificar que abre `TagGroupsDialog`
- [ ] **Test 1.1.5:** Verificar que el diálogo tiene título correcto
- [ ] **Test 1.1.6:** Verificar que se muestran grupos existentes (si hay)

**Resultado esperado:** Diálogo se abre correctamente con lista de grupos

---

### 1.2 Crear Tag Group

- [ ] **Test 1.2.1:** Click en botón "+ Nuevo Grupo"
- [ ] **Test 1.2.2:** Verificar que abre `TagGroupEditorDialog`
- [ ] **Test 1.2.3:** Verificar que todos los campos están vacíos
- [ ] **Test 1.2.4:** Intentar guardar sin llenar campos → Debe mostrar error
- [ ] **Test 1.2.5:** Llenar nombre: "Test Manual Group"
- [ ] **Test 1.2.6:** Click en selector de icono
- [ ] **Test 1.2.7:** Verificar que muestra grid de 30 emojis
- [ ] **Test 1.2.8:** Seleccionar icono 🐍
- [ ] **Test 1.2.9:** Click en selector de color
- [ ] **Test 1.2.10:** Seleccionar color azul (#3776ab)
- [ ] **Test 1.2.11:** Llenar tags: "python, pytest, testing, automation"
- [ ] **Test 1.2.12:** Verificar vista previa de tags (chips coloridos)
- [ ] **Test 1.2.13:** Llenar descripción: "Grupo de prueba manual"
- [ ] **Test 1.2.14:** Click en "Guardar"
- [ ] **Test 1.2.15:** Verificar que el diálogo se cierra
- [ ] **Test 1.2.16:** Verificar que el nuevo grupo aparece en la lista
- [ ] **Test 1.2.17:** Verificar que muestra icono, nombre, tags correctos

**Resultado esperado:** Grupo se crea correctamente y aparece en lista

---

### 1.3 Editar Tag Group

- [ ] **Test 1.3.1:** Click en botón "Editar" (✏️) de un grupo existente
- [ ] **Test 1.3.2:** Verificar que abre editor con datos cargados
- [ ] **Test 1.3.3:** Modificar nombre agregando " - Editado"
- [ ] **Test 1.3.4:** Agregar tag nuevo: "mock"
- [ ] **Test 1.3.5:** Cambiar descripción
- [ ] **Test 1.3.6:** Click en "Guardar"
- [ ] **Test 1.3.7:** Verificar que cambios se reflejan en lista
- [ ] **Test 1.3.8:** Reabrir editor y verificar que cambios persisten

**Resultado esperado:** Cambios se guardan y persisten correctamente

---

### 1.4 Eliminar Tag Group

- [ ] **Test 1.4.1:** Click en botón "Eliminar" (🗑️) de un grupo
- [ ] **Test 1.4.2:** Verificar que muestra diálogo de confirmación
- [ ] **Test 1.4.3:** Click en "Cancelar" → Grupo NO se elimina
- [ ] **Test 1.4.4:** Click en "Eliminar" nuevamente
- [ ] **Test 1.4.5:** Click en "Confirmar" → Grupo se elimina
- [ ] **Test 1.4.6:** Verificar que grupo desaparece de la lista

**Resultado esperado:** Grupo se elimina solo después de confirmación

---

### 1.5 Búsqueda de Tag Groups

- [ ] **Test 1.5.1:** Escribir término en barra de búsqueda
- [ ] **Test 1.5.2:** Verificar que lista se filtra en tiempo real
- [ ] **Test 1.5.3:** Verificar que busca en nombre
- [ ] **Test 1.5.4:** Verificar que busca en tags
- [ ] **Test 1.5.5:** Borrar búsqueda → Todos los grupos reaparecen
- [ ] **Test 1.5.6:** Buscar término que no existe → Lista vacía con mensaje

**Resultado esperado:** Búsqueda filtra correctamente en tiempo real

---

### 1.6 Estadísticas y Conteo de Uso

- [ ] **Test 1.6.1:** Verificar que cada Tag Group muestra "📊 Usado en X items"
- [ ] **Test 1.6.2:** Crear item nuevo con tags de un grupo
- [ ] **Test 1.6.3:** Reabrir Tag Groups Manager
- [ ] **Test 1.6.4:** Verificar que el conteo aumentó
- [ ] **Test 1.6.5:** Eliminar item → Conteo debe disminuir

**Resultado esperado:** Conteo de uso es preciso y se actualiza

---

### 1.7 Validaciones

- [ ] **Test 1.7.1:** Intentar crear grupo sin nombre → Error
- [ ] **Test 1.7.2:** Intentar crear grupo sin tags → Error
- [ ] **Test 1.7.3:** Intentar crear grupo con nombre duplicado → Error
- [ ] **Test 1.7.4:** Intentar tags con solo comas ",,," → Error
- [ ] **Test 1.7.5:** Verificar que mensajes de error son claros

**Resultado esperado:** Validaciones funcionan y muestran mensajes claros

---

## 🔍 SECCIÓN 2: Smart Collections Manager

### 2.1 Acceso al Manager

- [ ] **Test 2.1.1:** Abrir Settings → General
- [ ] **Test 2.1.2:** Verificar sección "🔍 Colecciones Inteligentes"
- [ ] **Test 2.1.3:** Click en "📋 Gestionar Colecciones Inteligentes"
- [ ] **Test 2.1.4:** Verificar que abre `SmartCollectionsDialog`
- [ ] **Test 2.1.5:** Verificar que muestra colecciones existentes (si hay)

**Resultado esperado:** Diálogo se abre con lista de colecciones

---

### 2.2 Crear Smart Collection Básica

- [ ] **Test 2.2.1:** Click en "+ Nueva Colección"
- [ ] **Test 2.2.2:** Verificar que abre `SmartCollectionEditorDialog`
- [ ] **Test 2.2.3:** Llenar nombre: "Test Manual Collection"
- [ ] **Test 2.2.4:** Seleccionar icono 🔍
- [ ] **Test 2.2.5:** Seleccionar color verde
- [ ] **Test 2.2.6:** En sección "Tags", llenar incluir: "python, api"
- [ ] **Test 2.2.7:** Verificar que vista previa muestra "📊 X items coinciden"
- [ ] **Test 2.2.8:** Esperar 500ms y verificar que contador se actualiza
- [ ] **Test 2.2.9:** Click en "Crear"
- [ ] **Test 2.2.10:** Verificar que colección aparece en lista con conteo correcto

**Resultado esperado:** Colección básica se crea con filtros funcionando

---

### 2.3 Crear Smart Collection con Múltiples Filtros

- [ ] **Test 2.3.1:** Crear nueva colección
- [ ] **Test 2.3.2:** Llenar nombre: "Test Advanced Filters"
- [ ] **Test 2.3.3:** Tags incluir: "python, fastapi"
- [ ] **Test 2.3.4:** Tags excluir: "deprecated"
- [ ] **Test 2.3.5:** Seleccionar tipo: CODE
- [ ] **Test 2.3.6:** Seleccionar categoría específica
- [ ] **Test 2.3.7:** Marcar checkbox "Solo favoritos"
- [ ] **Test 2.3.8:** Marcar checkbox "Solo activos"
- [ ] **Test 2.3.9:** Verificar que vista previa se actualiza con cada cambio
- [ ] **Test 2.3.10:** Guardar y verificar que funciona correctamente

**Resultado esperado:** Filtros múltiples se combinan con lógica AND

---

### 2.4 Filtros por Fecha

- [ ] **Test 2.4.1:** Crear nueva colección
- [ ] **Test 2.4.2:** Activar checkbox "Fecha desde"
- [ ] **Test 2.4.3:** Seleccionar fecha hace 30 días
- [ ] **Test 2.4.4:** Activar checkbox "Fecha hasta"
- [ ] **Test 2.4.5:** Seleccionar fecha hoy
- [ ] **Test 2.4.6:** Verificar que vista previa filtra por fechas
- [ ] **Test 2.4.7:** Guardar y verificar resultados

**Resultado esperado:** Filtros de fecha funcionan correctamente

---

### 2.5 Vista Previa en Tiempo Real

- [ ] **Test 2.5.1:** Abrir editor de colección
- [ ] **Test 2.5.2:** Escribir en campo de tags
- [ ] **Test 2.5.3:** Verificar que hay delay de ~500ms antes de actualizar
- [ ] **Test 2.5.4:** Verificar que contador cambia después del delay
- [ ] **Test 2.5.5:** Cambiar múltiples filtros rápidamente
- [ ] **Test 2.5.6:** Verificar que solo se ejecuta una vez después del delay

**Resultado esperado:** Debounce funciona, no hay lag ni queries excesivas

---

### 2.6 Editar Smart Collection

- [ ] **Test 2.6.1:** Click en "Editar" de una colección
- [ ] **Test 2.6.2:** Verificar que todos los filtros se cargan correctamente
- [ ] **Test 2.6.3:** Modificar nombre
- [ ] **Test 2.6.4:** Cambiar filtros de tags
- [ ] **Test 2.6.5:** Modificar tipo de item
- [ ] **Test 2.6.6:** Guardar cambios
- [ ] **Test 2.6.7:** Verificar que cambios se reflejan
- [ ] **Test 2.6.8:** Verificar que conteo de items se actualiza

**Resultado esperado:** Edición funciona y filtros se actualizan

---

### 2.7 Eliminar Smart Collection

- [ ] **Test 2.7.1:** Click en "Eliminar" de una colección
- [ ] **Test 2.7.2:** Verificar diálogo de confirmación
- [ ] **Test 2.7.3:** Cancelar → No se elimina
- [ ] **Test 2.7.4:** Confirmar → Se elimina
- [ ] **Test 2.7.5:** Verificar que desaparece de lista

**Resultado esperado:** Eliminación funciona con confirmación

---

### 2.8 Ver Items de Colección

- [ ] **Test 2.8.1:** Click en "Ver Items" (👁️) de una colección
- [ ] **Test 2.8.2:** Verificar que muestra lista de items que cumplen filtros
- [ ] **Test 2.8.3:** Verificar que todos los items mostrados cumplen criterios
- [ ] **Test 2.8.4:** Click en un item → Debe copiarse al portapapeles
- [ ] **Test 2.8.5:** Verificar que conteo coincide con vista previa

**Resultado esperado:** Vista de items funciona y muestra resultados correctos

---

### 2.9 Búsqueda de Colecciones

- [ ] **Test 2.9.1:** Escribir en barra de búsqueda
- [ ] **Test 2.9.2:** Verificar filtrado en tiempo real
- [ ] **Test 2.9.3:** Buscar por nombre de colección
- [ ] **Test 2.9.4:** Buscar por tags en descripción
- [ ] **Test 2.9.5:** Borrar búsqueda → Todas reaparecen

**Resultado esperado:** Búsqueda funciona correctamente

---

## 🎨 SECCIÓN 3: Tag Group Selector en Item Editor

### 3.1 Acceso al Selector

- [ ] **Test 3.1.1:** Abrir editor de item (Nuevo Item o Editar Item)
- [ ] **Test 3.1.2:** Verificar que existe widget "Tag Group Selector"
- [ ] **Test 3.1.3:** Verificar que está debajo del campo de tags
- [ ] **Test 3.1.4:** Verificar que muestra dropdown de grupos

**Resultado esperado:** Selector está presente y visible

---

### 3.2 Seleccionar Tag Group

- [ ] **Test 3.2.1:** Click en dropdown de Tag Groups
- [ ] **Test 3.2.2:** Verificar que lista todos los grupos activos
- [ ] **Test 3.2.3:** Seleccionar un grupo
- [ ] **Test 3.2.4:** Verificar que campo de tags se llena automáticamente
- [ ] **Test 3.2.5:** Verificar que tags están en formato "tag1, tag2, tag3"

**Resultado esperado:** Tags se aplican automáticamente al seleccionar grupo

---

### 3.3 Modificar Tags Después de Selección

- [ ] **Test 3.3.1:** Seleccionar Tag Group
- [ ] **Test 3.3.2:** Editar manualmente el campo de tags
- [ ] **Test 3.3.3:** Agregar tag adicional
- [ ] **Test 3.3.4:** Eliminar algún tag del grupo
- [ ] **Test 3.3.5:** Guardar item
- [ ] **Test 3.3.6:** Reabrir → Verificar que tags personalizados se guardaron

**Resultado esperado:** Puedes modificar tags después de usar grupo

---

### 3.4 Botón "Gestionar Grupos"

- [ ] **Test 3.4.1:** Click en botón "Gestionar Tag Groups"
- [ ] **Test 3.4.2:** Verificar que abre Tag Groups Manager
- [ ] **Test 3.4.3:** Crear nuevo grupo desde ahí
- [ ] **Test 3.4.4:** Cerrar manager y volver al editor
- [ ] **Test 3.4.5:** Verificar que dropdown se actualizó con nuevo grupo

**Resultado esperado:** Puedes gestionar grupos sin salir del editor

---

### 3.5 Cargar Tags Existentes

- [ ] **Test 3.5.1:** Abrir item existente con tags
- [ ] **Test 3.5.2:** Verificar que campo de tags muestra tags correctos
- [ ] **Test 3.5.3:** Verificar que selector NO selecciona grupo automáticamente
- [ ] **Test 3.5.4:** Seleccionar un grupo → Reemplaza tags actuales
- [ ] **Test 3.5.5:** Deshacer (Ctrl+Z) → Tags anteriores reaparecen

**Resultado esperado:** Edición de items existentes funciona correctamente

---

## 🔄 SECCIÓN 4: Integración y Flujos Completos

### 4.1 Flujo: Crear Grupo → Crear Item → Crear Colección

- [ ] **Test 4.1.1:** Crear Tag Group "Test Flow" con tags "test, flow, e2e"
- [ ] **Test 4.1.2:** Crear nuevo item usando ese Tag Group
- [ ] **Test 4.1.3:** Verificar que tags se aplicaron al item
- [ ] **Test 4.1.4:** Guardar item
- [ ] **Test 4.1.5:** Crear Smart Collection filtrando por esos tags
- [ ] **Test 4.1.6:** Verificar que la colección encuentra el item
- [ ] **Test 4.1.7:** Editar item y cambiar tags
- [ ] **Test 4.1.8:** Reabrir colección → Item ya no aparece (si no cumple filtros)

**Resultado esperado:** Flujo completo funciona end-to-end

---

### 4.2 Flujo: Actualización en Tiempo Real

- [ ] **Test 4.2.1:** Abrir Smart Collections Manager
- [ ] **Test 4.2.2:** Anotar conteo de items en una colección
- [ ] **Test 4.2.3:** Crear nuevo item que cumpla filtros de esa colección
- [ ] **Test 4.2.4:** Reabrir Smart Collections Manager
- [ ] **Test 4.2.5:** Verificar que conteo aumentó
- [ ] **Test 4.2.6:** Eliminar item
- [ ] **Test 4.2.7:** Reabrir manager → Conteo disminuyó

**Resultado esperado:** Colecciones se actualizan dinámicamente con cambios

---

### 4.3 Flujo: Migración de Tags

- [ ] **Test 4.3.1:** Ejecutar `python util/migrations/analyze_existing_tags.py`
- [ ] **Test 4.3.2:** Revisar reporte generado
- [ ] **Test 4.3.3:** Ejecutar `python util/migrations/migrate_to_tag_groups.py --dry-run`
- [ ] **Test 4.3.4:** Revisar cambios propuestos
- [ ] **Test 4.3.5:** Ejecutar migración real
- [ ] **Test 4.3.6:** Abrir aplicación
- [ ] **Test 4.3.7:** Verificar Tag Groups creados automáticamente
- [ ] **Test 4.3.8:** Verificar que tags en items están normalizados
- [ ] **Test 4.3.9:** Crear Smart Collection usando tags normalizados
- [ ] **Test 4.3.10:** Verificar que encuentra items correctamente

**Resultado esperado:** Migración funciona y datos quedan consistentes

---

## 🎯 SECCIÓN 5: Casos Edge y Errores

### 5.1 Manejo de Datos Vacíos

- [ ] **Test 5.1.1:** Abrir Tag Groups Manager en DB nueva (sin grupos)
- [ ] **Test 5.1.2:** Verificar mensaje "No hay grupos" o lista vacía
- [ ] **Test 5.1.3:** Abrir Smart Collections Manager sin colecciones
- [ ] **Test 5.1.4:** Verificar mensaje apropiado
- [ ] **Test 5.1.5:** Crear item sin tags → Selector debe funcionar igual
- [ ] **Test 5.1.6:** Crear colección sin filtros → Debe mostrar todos los items

**Resultado esperado:** UI maneja estados vacíos correctamente

---

### 5.2 Validaciones de Límites

- [ ] **Test 5.2.1:** Intentar nombre de grupo muy largo (>100 chars)
- [ ] **Test 5.2.2:** Intentar tag muy largo (>50 chars)
- [ ] **Test 5.2.3:** Intentar muchos tags (>20) → Debe permitir pero advertir
- [ ] **Test 5.2.4:** Intentar crear 100+ Tag Groups → Debe funcionar
- [ ] **Test 5.2.5:** Buscar con caracteres especiales en búsqueda

**Resultado esperado:** Límites se respetan o muestran advertencias

---

### 5.3 Concurrencia y Conflictos

- [ ] **Test 5.3.1:** Abrir 2 ventanas de Tag Groups Manager
- [ ] **Test 5.3.2:** Crear grupo en ventana 1
- [ ] **Test 5.3.3:** Intentar crear grupo con mismo nombre en ventana 2
- [ ] **Test 5.3.4:** Debe mostrar error de duplicado
- [ ] **Test 5.3.5:** Editar grupo en ventana 1
- [ ] **Test 5.3.6:** Cerrar ventana 2 y reabrir → Ver cambios

**Resultado esperado:** Conflictos se manejan correctamente

---

### 5.4 Performance con Datos Grandes

- [ ] **Test 5.4.1:** Crear 50+ Tag Groups
- [ ] **Test 5.4.2:** Verificar que lista se renderiza rápido (<1s)
- [ ] **Test 5.4.3:** Buscar en lista grande → Debe ser instantáneo
- [ ] **Test 5.4.4:** Crear colección en DB con 500+ items
- [ ] **Test 5.4.5:** Vista previa debe actualizarse en <1s
- [ ] **Test 5.4.6:** Abrir dropdown de Tag Groups con 50+ grupos
- [ ] **Test 5.4.7:** Debe renderizarse sin lag

**Resultado esperado:** UI es responsive incluso con muchos datos

---

## 🐛 SECCIÓN 6: Regresión

### 6.1 Funcionalidad Existente No Afectada

- [ ] **Test 6.1.1:** Crear item SIN usar Tag Groups → Funciona igual
- [ ] **Test 6.1.2:** Editar item sin tocar tags → Se guarda correctamente
- [ ] **Test 6.1.3:** Copiar item al portapapeles → Funciona
- [ ] **Test 6.1.4:** Marcar item como favorito → Funciona
- [ ] **Test 6.1.5:** Búsqueda global de items → Funciona
- [ ] **Test 6.1.6:** Crear categoría → Funciona
- [ ] **Test 6.1.7:** Todos los hotkeys funcionan
- [ ] **Test 6.1.8:** Sistema tray funciona
- [ ] **Test 6.1.9:** Todas las otras settings funcionan

**Resultado esperado:** Nada se rompió con las nuevas features

---

## 📊 RESUMEN DE TESTING

**Total de tests:** ~150

### Por Sección:
- Tag Groups Manager: 35 tests
- Smart Collections Manager: 40 tests
- Tag Group Selector: 20 tests
- Integración: 20 tests
- Edge Cases: 20 tests
- Regresión: 15 tests

### Criterio de Aceptación:
- ✅ **PASS:** >= 95% de tests pasan (máximo 7 fallos permitidos)
- ⚠️ **CONDICIONAL:** 90-94% pasan (revisar fallos)
- ❌ **FAIL:** < 90% pasan (requiere fixes)

---

## 📝 Notas y Bugs Encontrados

### Bug #1
**Test:** [Número de test]
**Descripción:** [Qué pasó]
**Pasos para reproducir:**
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Resultado esperado:** [Qué debería pasar]
**Resultado actual:** [Qué pasó]
**Severidad:** [Crítico / Alto / Medio / Bajo]
**Screenshot:** [Ruta al screenshot si aplica]

---

### Bug #2
...

---

## ✅ Checklist de Aprobación Final

- [ ] Todos los tests críticos pasan
- [ ] No hay bugs de severidad crítica
- [ ] Performance es aceptable (< 1s para operaciones comunes)
- [ ] UI es consistente con el resto de la app
- [ ] No hay regresiones en funcionalidad existente
- [ ] Documentación está actualizada
- [ ] Tests automatizados pasan

---

**Tester:** _______________
**Fecha:** _______________
**Resultado:** PASS / FAIL
**Comentarios:** _______________

---

**Versión del documento:** 1.0
**Última actualización:** 2025-11-05
