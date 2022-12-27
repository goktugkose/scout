FROM python:3.10.4
RUN python -m pip install pip==20.0.2
RUN apt-get update && apt-get install -y --no-install-recommends \
  gnupg2 \
  gcc \
  g++ \
  unixodbc \
  unixodbc-dev \
  libpq-dev \ 
  ca-certificates wget

RUN apt-get clean
RUN wget -O- https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN wget -O- https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN ACCEPT_EULA=Y apt-get -y install mssql-tools

WORKDIR /ws-user-stories
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .