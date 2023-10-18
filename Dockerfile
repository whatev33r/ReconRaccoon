FROM python:3.11

RUN useradd --create-home reconraccoon_user

RUN apt-get update

ENV PATH="/home/reconraccoon_user/.local/bin:${PATH}"

COPY . /reconraccoon
WORKDIR /reconraccoon

RUN chown -R reconraccoon_user:reconraccoon_user /reconraccoon
USER reconraccoon_user

RUN pip install --upgrade pip setuptools --user && \
    pip install -r requirements.txt --user
