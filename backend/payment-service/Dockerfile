FROM maven:3.9.5-eclipse-temurin-17 AS build

WORKDIR /app

# Copy and build shared common module first
COPY shared/common /app/shared/common
WORKDIR /app/shared/common
RUN mvn clean install -DskipTests

# Copy and build payment service
WORKDIR /app
COPY backend/payment-service/pom.xml ./payment-service/pom.xml
COPY backend/payment-service/src ./payment-service/src
WORKDIR /app/payment-service
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=build /app/payment-service/target/*.jar app.jar

EXPOSE 8084

ENTRYPOINT ["java", "-jar", "app.jar"]
