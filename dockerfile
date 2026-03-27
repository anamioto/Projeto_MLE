# Imagem base oficial da AWS para Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Instala as dependências de ML
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copia o código e o modelo para os diretórios esperados
COPY src/app.py ${LAMBDA_TASK_ROOT}
COPY modelo/model.pkl ${LAMBDA_TASK_ROOT}/modelo/

# Define o entrypoint da função
CMD [ "app.lambda_handler" ]
