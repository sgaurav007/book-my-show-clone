FROM eclipse-temurin:17-jdk-alpine AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN apk add --no-cache maven && \
    mvn clean package -DskipTests && \
    apk del maven

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

COPY --from=build /app/target/notification-service-1.0.0.jar app.jar

EXPOSE 8084

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8084/api/notifications/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]

ENV JAVA_OPTS="-Xmx512m -Xms256m" \
    SPRING_PROFILES_ACTIVE="prod"

CMD ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
