# https://hub.docker.com/_/ubuntu
FROM ubuntu:22.04

# Expose port for Docker (our default for microservices is 80)
EXPOSE 80

# Inject conda packages by the CI/CD pipeline to run 'conda create env' only once
ENV PATH=/opt/conda/bin:$PATH
COPY /opt/conda/ /opt/conda/

COPY topic_modeling /topic_modeling
ENTRYPOINT ["python", "/topic_modeling"]
