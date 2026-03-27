# Projeto MLE: Titanic Survival Prediction API (IaC)

Este repositório contém a implementação de uma arquitetura de Machine Learning voltada para produção (ML Engineering), expondo um modelo de predição de sobrevivência do Titanic através de uma API Serverless na AWS. Todo o provisionamento da infraestrutura é realizado de forma automatizada via **Terraform (IaC)**.

## 🚀 Objetivo
O objetivo deste projeto é demonstrar o ciclo completo de deployment de um modelo:
1.  **Modelo:** Predição de sobrevivência (Titanic dataset).
2.  **API:** Interface REST para consumo do modelo.
3.  **Cloud:** Arquitetura Serverless de baixo custo e alta escalabilidade.
4.  **IaC:** Garantir que toda a infraestrutura seja replicável e versionada.

## 🏗️ Arquitetura

A solução utiliza os seguintes serviços da AWS:
-   **API Gateway:** Ponto de entrada para as requisições HTTP.
-   **AWS Lambda:** Execução do código Python com a lógica de inferência.
-   **DynamoDB:** Armazenamento de logs de predições para monitoramento futuro.
-   **Terraform:** Ferramenta de Infrastructure as Code para gerenciar os recursos.

## 📁 Estrutura do Repositório

```text
├── infraestrutura/                     # Arquivos de configuração da infraestrutura (.tf)
│   ├── main.tf                         # Definição principal dos recursos
│   ├── lambda_function_payload.zip     # Definição principal dos recursos
│   ├── var.tfvars                      # Variáveis de configuração
│   ├── tfplan_final                    # Plano da infraestrutura (último rodado)
│   └── terraform.tfstate               # Estado atual da infraestrutura (o mesmo com .backup é uma cópia de segurança)
├── modelo/                             # Artefatos do modelo de ML
│   ├── debug_model.py                  # Código para verificar o modelo serializado
│   ├── treinamento.py                  # Código de treinamento do modelo
│   └── model.pkl                       # Modelo serializado (.pkl ou .joblib)
├── src/                                # Código fonte da aplicação
│   └── app.py                          # Handler principal da AWS Lambda
├── documentação/                       # Documentação OPENAPI 3.0
│   └── openapi.yaml                    # Documento de entrada da API
├── requirements.txt                    # Dependências do Python
├── dockerfile                          # Arquivo com os comandos docker para criação do container
└── README.md                           # Documentação completa do projeto
```

## 🛠️ Tecnologias Utilizadas
- Linguagem: Python
- Frameworks de ML: Scikit-learn
- Infraestrutura: Terraform, AWS CLI
- Serviços Cloud: AWS Lambda, API Gateway, DynamoDB, IAM

## 📈 Melhorias Futuras
1. Implantação do tratamento dos dados a serem recebidos
2. Implantação da correção dos tipos de dados a serem salvos no DynamoDB
3. Implementação de CI/CD via GitHub Actions.
4. Implementação do monitoramento e observabilidade.
