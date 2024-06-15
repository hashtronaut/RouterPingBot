FROM python:3.10-alpine
WORKDIR /bot
COPY dependencies.txt .
RUN pip install -r dependencies.txt
ADD . .
CMD ["python", "./bot.py"]
