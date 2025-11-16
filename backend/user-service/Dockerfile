FROM eclipse-temurin:17-jdk-alpine AS build

WORKDIR /app

COPY backend/user-service/pom.xml .
COPY backend/user-service/src ./src

RUN apk add --no-cache maven

RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
