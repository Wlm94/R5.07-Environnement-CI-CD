FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/spring-boot-service-*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]