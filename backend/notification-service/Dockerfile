FROM maven:3.9.5-eclipse-temurin-17 AS build

WORKDIR /app

# Copy and build shared common module first
COPY shared/common /app/shared/common
WORKDIR /app/shared/common
RUN mvn clean install -DskipTests

# Copy and build notification service
WORKDIR /app
COPY backend/notification-service/pom.xml ./notification-service/pom.xml
COPY backend/notification-service/src ./notification-service/src
WORKDIR /app/notification-service
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

COPY --from=build /app/notification-service/target/*.jar app.jar

EXPOSE 8085

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8085/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
