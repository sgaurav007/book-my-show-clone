FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

COPY backend/payment-service/pom.xml .
RUN mvn dependency:go-offline

COPY backend/payment-service/src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=build /app/target/payment-service-1.0.0.jar app.jar

EXPOSE 8084

ENTRYPOINT ["java", "-jar", "app.jar"]
