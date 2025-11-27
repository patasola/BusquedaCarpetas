# entrenador_ia.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle

class ClasificadorExpedientes:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier()
        
    def entrenar(self, historico_correos):
        """Entrena con tu histórico de correos ya clasificados"""
        # Extraer características de correos históricos
        textos = [c['asunto'] + ' ' + c['cuerpo'] for c in historico_correos]
        expedientes = [c['expediente'] for c in historico_correos]
        
        X = self.vectorizer.fit_transform(textos)
        self.classifier.fit(X, expedientes)
        
        # Guardar modelo
        with open('modelo_expedientes.pkl', 'wb') as f:
            pickle.dump((self.vectorizer, self.classifier), f)
    
    def predecir(self, asunto, cuerpo):
        """Predice el expediente más probable"""
        texto = asunto + ' ' + cuerpo
        X = self.vectorizer.transform([texto])
        prediccion = self.classifier.predict(X)[0]
        confianza = max(self.classifier.predict_proba(X)[0])
        
        if confianza > 0.8:  # Solo si está muy seguro
            return prediccion
        return None