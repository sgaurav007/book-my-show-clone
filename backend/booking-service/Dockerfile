# Multi-stage build for Booking Service
FROM maven:3.9.5-eclipse-temurin-17 AS build

WORKDIR /app

# Copy shared common module first
COPY shared/common /app/shared/common

# Build shared module
WORKDIR /app/shared/common
RUN mvn clean install -DskipTests

# Copy booking service
WORKDIR /app/booking-service
COPY backend/booking-service/pom.xml .
COPY backend/booking-service/src ./src

# Build booking service
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy the built JAR from build stage
COPY --from=build /app/booking-service/target/booking-service-1.0.0.jar app.jar

# Expose port
EXPOSE 8082

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8082/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
