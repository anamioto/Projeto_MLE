#Carregar as bibliotecas principais
import json
import os
import uuid
import joblib
import boto3
from decimal import Decimal
import numpy as np

# Configurações do ambiente
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'SobreviventesTitanic')
MODEL_PATH = './modelo/model.pkl'

# Inicialização de recursos (Fora do handler para reaproveitamento em Warm Starts)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# Carrega o modelo uma única vez na inicialização da instância da Lambda
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    model = None

# Configurações de validação baseadas no modelo
# Ordem e nomes conforme o treinamento: ['Pclass', 'SibSp', 'Age', 'Embarked_S', 'Sex_male', 'Parch', 'Embarked_Q', 'Fare']
EXPECTED_TYPES = [int, int, float, bool, bool, int, bool, float]
EXPECTED_COUNT = len(list(model.feature_names_in_))

def lambda_handler(event, context):
    """
    Handler principal que gerencia as rotas da API (POST, GET, DELETE)
    """
    http_method = event.get('httpMethod')
    path_parameters = event.get('pathParameters') or {}
    path = event.get("path", "")
    passenger_id = path_parameters.get('id')

    try:
        # --- ROTA: POST /sobreviventes ---
        if http_method == 'POST' and path == "/sobreviventes":
            body = json.loads(event.get('body', '{}'))
            features = body.get('features')

            # 1º Verificação de existência
            if not features:
                return response(400, {"error": "Features não fornecidas na requisição."})

            # 2º Verificação de Quantidade
            if len(features) != EXPECTED_COUNT:
                 return response(400, {
                      "error": "Quantidade de colunas inválida.",
                      "esperado": EXPECTED_COUNT,
                      "recebido": len(features)
                    })

            # 3º Verificação de Tipos (e conversão se necessário)
            validated_features = []
            try:
                for i, value in enumerate(features):
                    expected_type = EXPECTED_TYPES[i]
            
                    # Validação estrita de tipo
                    if expected_type == bool:
                        if not isinstance(value, bool):
                            raise TypeError(f"Coluna {i} ({model.feature_names_in_[i]}) deve ser Booleana.")
                    elif expected_type == int:
                        if not isinstance(value, (int, np.integer)):
                            raise TypeError(f"Coluna {i} ({model.feature_names_in_[i]}) deve ser Inteira.")
                    elif expected_type == float:
                        if not isinstance(value, (int, float, np.floating)):
                            raise TypeError(f"Coluna {i} ({model.feature_names_in_[i]}) deve ser decimal (float).")
            
                    validated_features.append(value)
            
            except (TypeError, ValueError) as e:
                return response(400, {"error": "Erro de tipagem nas features.", "Detalhes": str(e)})

            # Realiza a predição (probabilidade de sobrevivência)
            # O modelo geralmente retorna [[prob_morte, prob_sobrev]]
            prediction = model.predict_proba([validated_features])[0][1]
            
            new_id = str(uuid.uuid4())
            # Função auxiliar interna para garantir que o DynamoDB aceite os dados
            def to_dynamo_type(v):
                if isinstance(v, bool):
                     return v  # Booleanos são aceitos nativamente pelo DynamoDB
                if isinstance(v, (int, float, np.integer, np.floating)):
                     return Decimal(str(v)) # Converte números para Decimal via String (Seguro)
                return str(v) # Qualquer outra coisa vira String

            item = {
                'id': new_id,
                'probabilidade': Decimal(str(round(float(prediction), 4))),
                'features': [to_dynamo_type(f) for f in validated_features]
            }
            
            table.put_item(Item=item)
            return response(201, {"Passenger_id": new_id, "probabilidade_sobrevivencia": float(prediction)})

        # --- ROTA: GET /sobreviventes/{id} ---
        elif http_method == 'GET' and passenger_id:            
            res = table.get_item(Key={'id': passenger_id})
            if 'Item' in res:
                return response(200, res['Item'])
            return response(404, {"error": "Passageiro não encontrado."})

        # --- ROTA: GET /sobreviventes (Lista Todos) ---
        elif http_method == 'GET':
            res = table.scan() # Aceitável para baixo volume, como solicitado
            return response(200, res.get('Items', []))

        # --- ROTA: DELETE /sobreviventes/{id} ---
        elif http_method == 'DELETE' and passenger_id:
            # 1º Verifica se o passageiro existe primeiro
            existente = table.get_item(Key={'id': passenger_id})

            # 2ºa Caso não exista, irá apresentar o erro
            if 'Item' not in existente:
                return response(404, {"error": "Impossível deletar: ID não encontrado."})
            
            # 2ºb Caso exista, será deletado
            table.delete_item(Key={'id': passenger_id})
            return response(200, {"message": f"ID {passenger_id} deletado com sucesso."})

        return response(405, {"error": "Método não permitido."})

    except Exception as e:
        print(f"Erro interno: {e}")
        return response(500, {"error": str(e)})

def response(status_code, body):
    """Helper para formatar a resposta do API Gateway"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=str)
    }