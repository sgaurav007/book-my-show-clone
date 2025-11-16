FROM maven:3.9.5-eclipse-temurin-17 AS build

WORKDIR /app

# Copy and build shared common module first
COPY shared/common /app/shared/common
WORKDIR /app/shared/common
RUN mvn clean install -DskipTests

# Copy and build user service
WORKDIR /app
COPY backend/user-service/pom.xml ./user-service/pom.xml
COPY backend/user-service/src ./user-service/src
WORKDIR /app/user-service
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=build /app/user-service/target/*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
