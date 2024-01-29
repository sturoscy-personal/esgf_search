FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

COPY ./app ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]
