"""
Disease Predictor Module
Implements triage logic for disease prediction based on symptoms
"""

class DiseasePredictors:
    """
    Disease prediction and triage system based on symptom analysis
    """
    
    # Symptom to condition mapping
    SYMPTOM_CONDITIONS = {
        'fever': {
            'flu': 0.8,
            'cold': 0.5,
            'covid': 0.7,
            'malaria': 0.6,
        },
        'cough': {
            'cold': 0.9,
            'flu': 0.7,
            'covid': 0.8,
            'asthma': 0.6,
        },
        'headache': {
            'migraine': 0.7,
            'flu': 0.5,
            'stress': 0.8,
            'tension': 0.9,
        },
        'body_ache': {
            'flu': 0.9,
            'covid': 0.7,
            'exercise': 0.6,
            'fibromyalgia': 0.5,
        },
        'fatigue': {
            'anemia': 0.7,
            'depression': 0.8,
            'thyroid': 0.6,
            'covid': 0.5,
        },
        'shortness_of_breath': {
            'asthma': 0.9,
            'pneumonia': 0.8,
            'heart_disease': 0.7,
            'anxiety': 0.6,
        },
        'sore_throat': {
            'strep_throat': 0.8,
            'cold': 0.7,
            'flu': 0.6,
            'allergies': 0.5,
        },
    }
    
    URGENCY_LEVELS = {
        'critical': 'SEEK EMERGENCY CARE IMMEDIATELY',
        'high': 'CONSULT A DOCTOR SOON',
        'moderate': 'CONSULT A DOCTOR WITHIN DAYS',
        'low': 'MONITOR AND SELF-CARE',
    }
    
    CRITICAL_SYMPTOMS = [
        'chest_pain',
        'severe_shortness_of_breath',
        'unconsciousness',
        'severe_bleeding',
        'signs_of_stroke',
    ]
    
    @staticmethod
    def predict_disease(symptoms: list, age: int = None, medical_history: list = None) -> dict:
        """
        Predict possible diseases based on symptoms
        
        Args:
            symptoms: List of symptoms reported by user
            age: User's age
            medical_history: List of previous conditions
        
        Returns:
            Dictionary with prediction results and recommendations
        """
        if medical_history is None:
            medical_history = []
        
        # Check for critical symptoms
        for symptom in symptoms:
            if symptom in DiseasePredictors.CRITICAL_SYMPTOMS:
                return {
                    'urgency': 'critical',
                    'urgency_message': DiseasePredictors.URGENCY_LEVELS['critical'],
                    'possible_conditions': [],
                    'recommendation': 'This requires immediate medical attention. Call emergency services.',
                    'severity_score': 0.95,
                }
        
        # Calculate condition scores
        condition_scores = {}
        
        for symptom in symptoms:
            symptom_key = symptom.lower().replace(' ', '_')
            
            if symptom_key in DiseasePredictors.SYMPTOM_CONDITIONS:
                for condition, score in DiseasePredictors.SYMPTOM_CONDITIONS[symptom_key].items():
                    if condition not in condition_scores:
                        condition_scores[condition] = []
                    condition_scores[condition].append(score)
        
        # Calculate average scores
        final_scores = {}
        for condition, scores in condition_scores.items():
            final_scores[condition] = sum(scores) / len(scores)
        
        # Sort by score
        sorted_conditions = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Determine urgency
        urgency = DiseasePredictors._determine_urgency(
            symptoms, 
            sorted_conditions, 
            age, 
            medical_history
        )
        
        return {
            'urgency': urgency,
            'urgency_message': DiseasePredictors.URGENCY_LEVELS[urgency],
            'possible_conditions': [
                {'name': cond, 'confidence': f'{score*100:.1f}%'} 
                for cond, score in sorted_conditions
            ],
            'recommendation': DiseasePredictors._get_recommendation(urgency, sorted_conditions),
            'severity_score': sorted_conditions[0][1] if sorted_conditions else 0,
        }
    
    @staticmethod
    def _determine_urgency(symptoms: list, conditions: list, age: int = None, medical_history: list = None) -> str:
        """
        Determine urgency level based on symptoms and conditions
        """
        high_risk_symptoms = [
            'chest pain',
            'difficulty breathing',
            'sudden weakness',
            'confusion',
            'severe pain',
        ]
        
        # Check for high-risk symptoms
        for symptom in symptoms:
            if any(risk in symptom.lower() for risk in high_risk_symptoms):
                return 'high'
        
        # Check age-related risk factors
        if age and age > 65:
            if conditions and conditions[0][1] > 0.7:
                return 'high'
        
        # Check for serious conditions
        serious_conditions = [
            'heart_disease',
            'pneumonia',
            'stroke',
            'cancer',
        ]
        
        if conditions:
            condition_name = conditions[0][0]
            if any(serious in condition_name.lower() for serious in serious_conditions):
                if conditions[0][1] > 0.6:
                    return 'high'
        
        # Default logic
        if conditions and conditions[0][1] > 0.8:
            return 'moderate'
        elif conditions and conditions[0][1] > 0.5:
            return 'moderate'
        else:
            return 'low'
    
    @staticmethod
    def _get_recommendation(urgency: str, conditions: list) -> str:
        """
        Get specific recommendation based on urgency and conditions
        """
        recommendations = {
            'critical': 'Call 911 or your local emergency number immediately.',
            'high': 'Schedule a doctor\'s appointment within 24-48 hours. If symptoms worsen, seek immediate care.',
            'moderate': 'Schedule a doctor\'s appointment within a few days. Monitor your symptoms.',
            'low': 'Continue observing your symptoms. Use home remedies and rest. If symptoms persist, consult a doctor.',
        }
        
        base_recommendation = recommendations.get(urgency, recommendations['low'])
        
        if conditions:
            base_recommendation += f"\n\nMost likely condition: {conditions[0][0].replace('_', ' ').title()}"
        
        return base_recommendation
    
    @staticmethod
    def get_symptom_checklist() -> dict:
        """
        Get common symptom categories for UI
        """
        return {
            'respiratory': ['Cough', 'Shortness of breath', 'Sore throat', 'Congestion'],
            'systemic': ['Fever', 'Fatigue', 'Body ache', 'Chills'],
            'neurological': ['Headache', 'Dizziness', 'Confusion', 'Loss of consciousness'],
            'digestive': ['Nausea', 'Vomiting', 'Diarrhea', 'Abdominal pain'],
            'cardiac': ['Chest pain', 'Irregular heartbeat', 'Shortness of breath'],
        }
