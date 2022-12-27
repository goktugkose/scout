FROM python:3.9.1 as py
WORKDIR /app
RUN apt-get update \
  && apt-get -y install gcc \
  && apt-get -y install g++ \
  && apt-get -y install unixodbc unixodbc-dev \
  && apt-get clean
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN apt-get -y install unixodbc-dev
RUN ACCEPT_EULA=Y apt-get -y install mssql-tools

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /app

COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o /app/published-app

# Build runtime image
FROM mcr.microsoft.com/dotnet/sdk:6.0 as runtime
WORKDIR /app
COPY --from=build /app/published-app /app
COPY --from=py . /app
ENV ASPNETCORE_URLS="http://*:5000"
ENTRYPOINT ["dotnet", "/app/wp-user-stories-dotnet-core.dll"]