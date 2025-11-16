FROM eclipse-temurin:17-jdk-alpine AS builder

WORKDIR /app

# Copy shared common module
COPY shared/common /app/shared/common

# Build shared common module
WORKDIR /app/shared/common
RUN ./mvnw clean install -DskipTests

# Copy catalog service
WORKDIR /app
COPY backend/catalog-service /app/catalog-service

# Build catalog service
WORKDIR /app/catalog-service
RUN ./mvnw clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=builder /app/catalog-service/target/*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
