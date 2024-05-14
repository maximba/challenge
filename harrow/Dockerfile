ARG pyvers
FROM python:$pyvers
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY harrow.py ./
CMD [ "python", "./harrow.py" ]
