# Dockerfile for app service
FROM python:3.10-slim

WORKDIR /app

RUN pip install streamlit

COPY . /app

EXPOSE 8501