import joblib
import pandas as pd

model = joblib.load("modelo/model.pkl")
print(type(model))

#validar as colunas esperadas
if hasattr(model, "feature_names_in_"):
    expected_features = list(model.feature_names_in_)
    print("Features esperadas:", expected_features)
else:
    expected_features = None
    print("O modelo não possui 'feature_names_in_'.")

#exemplo de input 
sample_input = {
    "Age": 29,
    "Fare": 80.0,
    "Parch": 0,
    "Embarked_S": True,
    "Pclass": 1,
    "Sex_male": False,
    "Embarked_Q": False,
    "SibSp": 1
}

if expected_features is not None:
    missing = [col for col in expected_features if col not in sample_input]
    if missing:
        raise ValueError(f"Faltam colunas no sample_input: {missing}")

    X_test = pd.DataFrame([[sample_input[col] for col in expected_features]], columns=expected_features)
else:
    X_test = pd.DataFrame([sample_input])

print("\nDataFrame de teste:")
print(X_test)

#testa predict
try:
    pred = model.predict(X_test)
    print("\nResultado do predict:", pred)
except Exception as e:
    print("\nErro no predict:", e)

# testa predict_proba, se existir
if hasattr(model, "predict_proba"):
    try:
        proba = model.predict_proba(X_test)
        print("\nResultado do predict_proba:")
        print(proba)
    except Exception as e:
        print("\nErro no predict_proba:", e)
else:
    print("\nO modelo não possui predict_proba.")