# EPICA-E[XXX]: [Nombre de la Épica]

## 📝 Descripción de la Épica
Como **[rol de usuario]**, necesito [funcionalidad principal] para [objetivo de negocio/valor].

## 🎯 Objetivos de Negocio
- [Objetivo específico 1]
- [Objetivo específico 2]
- [Objetivo específico 3]
- [Beneficio cuantificable]

## 📊 Información General
- **Epic ID**: EPICA-E[XXX]
- **Rol**: [👑/🎓/👨‍🏫/👨‍🎓/🤖] [ROL]
- **Prioridad**: [🔴 Must Have/🟡 Should Have/🟢 Could Have]
- **Story Points**: [XX] SP
- **Sprint Goal**: S[X]-S[Y] ([Z] semanas)
- **Dependencias**: [Lista de épicas dependientes]

## 👥 Stakeholders
- **Product Owner**: [Nombre del PO]
- **End Users**: [Lista de usuarios finales]
- **Development Team**: [Roles técnicos involucrados]

## 🎬 User Stories

### **US-[XX].1: [Nombre de la User Story]** ([XX] SP)
**Como** [tipo de usuario]  
**Quiero** [funcionalidad específica]  
**Para** [beneficio/valor obtenido]  

#### **Criterios de Aceptación**
- [ ] [Criterio específico y medible 1]
- [ ] [Criterio específico y medible 2]
- [ ] [Criterio específico y medible 3]
- [ ] [Criterio específico y medible 4]
- [ ] [Criterio específico y medible 5]
- [ ] [Criterio específico y medible 6]

#### **Definición de Listo**
- [ ] Código implementado y revisado
- [ ] Tests unitarios e integración >85% coverage
- [ ] Documentación técnica actualizada
- [ ] Revisión de código aprobada
- [ ] Testing de aceptación completado
- [ ] Desplegado en ambiente de testing

---

### **US-[XX].2: [Segunda User Story]** ([XX] SP)
[Repetir estructura anterior para cada user story]

---

## 🔧 Consideraciones Técnicas

### **Modelo de Datos**
```python
class [ModelName](models.Model):
    # Definir campos del modelo
    field1 = models.CharField(max_length=100)
    field2 = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "[Nombre del modelo]"
        ordering = ['-created_at']
```

### **API Endpoints**
```yaml
[Categoría]:
  GET    /api/[resource]/           # Lista recursos
  POST   /api/[resource]/           # Crear recurso
  GET    /api/[resource]/{id}/      # Obtener recurso específico
  PUT    /api/[resource]/{id}/      # Actualizar recurso
  DELETE /api/[resource]/{id}/      # Eliminar recurso
```

### **Frontend Components**
```javascript
const [ComponentName] = {
  // Descripción del componente
  features: ['feature1', 'feature2', 'feature3'],
  dependencies: ['dependency1', 'dependency2'],
  performance: {
    loadTime: '<2s',
    renderTime: '<500ms'
  }
}
```

## 🧪 Casos de Prueba

### **Test Suite: [Categoría de Tests]**
```python
class [TestCaseName](TestCase):
    def test_[specific_functionality](self):
        # Test específico de funcionalidad
        pass
    
    def test_[error_handling](self):
        # Test de manejo de errores
        pass
    
    def test_[edge_cases](self):
        # Test de casos extremos
        pass
```

### **Test Suite: [Segunda Categoría]**
```python
class [SecondTestCase](TestCase):
    def test_[integration_feature](self):
        # Test de integración
        pass
```

## 🚀 Criterios de Aceptación de la Épica

### **Funcionales**
- [ ] [Criterio funcional específico 1]
- [ ] [Criterio funcional específico 2]
- [ ] [Criterio funcional específico 3]
- [ ] [Criterio funcional específico 4]
- [ ] [Criterio funcional específico 5]

### **No Funcionales**
- [ ] Tiempo de respuesta < [X] segundos
- [ ] Disponibilidad > [X]%
- [ ] Escalabilidad: soporta [X]+ usuarios concurrentes
- [ ] Usabilidad: interfaz intuitiva y responsive
- [ ] Seguridad: [estándares específicos]
- [ ] Rendimiento: [métricas específicas]

### **Técnicos**
- [ ] Cobertura de tests > [X]%
- [ ] Documentación API completa
- [ ] Logs de auditoría implementados
- [ ] Manejo de errores robusto
- [ ] Validación de entrada en todos los endpoints
- [ ] Cumplimiento de estándares de codificación

## 📈 Métricas de Éxito

### **KPIs Funcionales**
- **[Métrica 1]**: >[X]% o <[Y] [unidad]
- **[Métrica 2]**: >[X] [unidad] por [período]
- **[Métrica 3]**: <[X]% [tipo de error]
- **[Métrica 4]**: >[X]/5 en [aspecto]

### **KPIs Técnicos**
- **Uptime**: >[X]%
- **Tiempo de respuesta**: <[X]ms
- **Errores de sistema**: <[X]%
- **Cobertura de tests**: >[X]%

## 🔄 Retrospectiva y Mejoras

### **Preguntas para Retrospectiva**
1. ¿[Pregunta específica sobre funcionalidad]?
2. ¿[Pregunta sobre experiencia de usuario]?
3. ¿[Pregunta sobre aspectos técnicos]?
4. ¿[Pregunta sobre mejoras futuras]?

### **Posibles Mejoras Futuras**
- [Mejora específica 1]
- [Mejora específica 2]
- [Mejora específica 3]
- [Integración con sistemas externos]
- [Optimizaciones de performance]

---

## 📚 Recursos y Referencias

### **Documentación Técnica**
- [Link a documentación técnica relevante]
- [Estándares de la industria]
- [Best practices aplicables]

### **Herramientas de Desarrollo**
- **Testing**: [herramientas específicas]
- **Framework**: [tecnologías utilizadas]
- **API**: [herramientas de API]
- **Frontend**: [frameworks frontend]

### **Compliance y Seguridad**
- **[Estándar 1]**: [Descripción de compliance]
- **[Estándar 2]**: [Prácticas de seguridad]
- **[Regulación]**: [Cumplimiento regulatorio]

---

**Notas de Implementación:**
- [Nota específica sobre implementación]
- [Consideración especial de diseño]
- [Limitación conocida o workaround] 