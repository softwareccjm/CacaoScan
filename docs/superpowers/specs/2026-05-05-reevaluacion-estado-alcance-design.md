# Reevaluación · Estado y Alcance del Sistema CacaoScan

**Fecha:** 2026-05-05
**Audiencia:** Ingenieros agroindustriales (saben de cacao y procesos, no de software)
**Destino:** Subpágina nueva en la página Notion `CacaoScan` (id `35770a22-2b3d-805e-893c-c03f125c62e8`)
**Propósito:** Dejar claro dónde estamos, el alcance actual, qué continuamos y qué integramos como Fase 2, con métricas reales del modelo, antes de la reevaluación.

## Estructura de la subpágina

### 1. Resumen ejecutivo
Callout azul, dos párrafos:
- CacaoScan: herramienta digital que mide el grano de cacao a partir de una foto, sin calibrador ni balanza.
- Para quién: agricultores, técnicos y comercializadores que necesitan caracterizar su lote rápidamente.

### 2. Dónde estamos hoy
Lista de módulos en operación:
- Captura de imagen del grano desde web/móvil
- Segmentación automática (recorte por visión computacional)
- Medición dimensional: largo, ancho, grosor (mm)
- Estimación de peso (g) por modelo predictivo
- Gestión de fincas, lotes y agricultores
- Generación de reportes (Excel/PDF)
- Historial y búsqueda de análisis

### 3. Efectividad actual del modelo
Tabla con métricas reales del último entrenamiento (98 granos evaluados, fuente: `evaluation_report_20251120_152747.json`):

| Variable | Error medio | Error relativo | Confiabilidad (R²) | Lectura |
|---|---|---|---|---|
| Largo | ±0.86 mm | 3.56% | 79% | Bueno |
| Ancho | ±0.54 mm | 4.52% | 84% | Bueno |
| Grosor | ±0.98 mm | 11.00% | 3% | Débil — replantear |
| Peso estimado | ±0.17 g | 10.03% | 57% | Moderado |

Lectura agroindustrial: largo y ancho confiables; grosor y peso necesitan más muestras y mejor calibración (la cámara captura 2D, el grosor es la dimensión perpendicular al lente — la más difícil de estimar sin profundidad).

### 4. Alcance actual: qué SÍ y qué NO hace

| ✅ Sí hace hoy | ❌ No hace todavía |
|---|---|
| Mide largo, ancho, grosor en mm | No clasifica fermentación (corte de grano) |
| Estima peso por imagen | No detecta defectos (mohoso, pizarroso, violeta) |
| Distingue grano sobre fondo | No mide humedad ni grasa |
| Genera reportes por lote | No identifica variedad (CCN-51, ICS, etc.) |
| Maneja múltiples fincas/agricultores | No conecta con sondas IoT de fermentación |

### 5. Lo que continuamos (Fase 1 — afinamiento)
- Mejorar modelo de grosor y peso con más muestras y nueva calibración
- Robustecer captura: guías visuales para foto consistente (distancia, luz, fondo)
- Mejorar reportes con gráficas comparativas por lote
- Pulir UX y acceso móvil
- Cerrar pruebas automatizadas y SonarQube al 100%

### 6. Lo que integramos nuevo (Fase 2 — clasificación de calidad NTC 1252)
- Clasificación de fermentación por imagen del corte longitudinal
- Detección de defectos visibles (mohoso, pizarroso, dañado por insecto, germinado)
- Identificación de variedad
- Cálculo de índice de grano (granos/100g) automático
- Posible integración futura con sondas IoT (poscosecha completa)

### 7. Preguntas para los evaluadores agroindustriales
Callout amarillo, abierto:
- ¿Qué tolerancia de error en milímetros y gramos consideran aceptable para uso comercial?
- ¿Qué normas priorizan: NTC 1252, FEDECACAO, ISO de comercio internacional, otra?
- ¿Qué variables agronómicas faltan que el sistema debería cubrir?
- ¿El índice de grano (granos por 100g) es la métrica más útil, o prefieren otra?
- ¿Para fermentación, prefieren clasificación por corte o por color exterior?
- ¿Qué información de lote/finca debería ir obligatoria en el reporte?

## Implementación
Crear la subpágina vía MCP de Notion (`notion-create-pages`) bajo el padre `CacaoScan`. Sin código en repo más allá de este spec.
