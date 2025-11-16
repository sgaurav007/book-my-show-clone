FROM maven:3.9.5-eclipse-temurin-17 AS builder

WORKDIR /app

# Copy and build shared common module
COPY shared/common /app/shared/common
WORKDIR /app/shared/common
RUN mvn clean install -DskipTests

# Copy and build catalog service
WORKDIR /app
COPY backend/catalog-service /app/catalog-service
WORKDIR /app/catalog-service
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=builder /app/catalog-service/target/*.jar app.jar

EXPOSE 8082

ENTRYPOINT ["java", "-jar", "app.jar"]
