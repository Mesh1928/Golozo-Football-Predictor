package GolozoBackend.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EntityScan(basePackages = "GolozoBackend.example.demo.predictionAI")
@EnableScheduling
public class GolApplication {
	public static void main(String[] args) {
		SpringApplication.run(GolApplication.class, args);
	}
}
