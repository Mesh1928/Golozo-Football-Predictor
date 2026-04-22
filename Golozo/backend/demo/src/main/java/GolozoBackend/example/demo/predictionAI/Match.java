package GolozoBackend.example.demo.predictionAI;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Setter
@Getter
@Entity
@Table(name = "matches", schema = "golozodb")
public class Match {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "season")
    private String season;

    @Column(name = "date")
    private LocalDate date;

    @Column(name = "team")
    private String team;

    @Column(name = "opponent")
    private String opponent;

    @Column(name = "venue")
    private String venue;

    @Column(name = "venue_code")
    private Integer venueCode;

    @Column(name = "opponent_code")
    private Integer opponentCode;

    @Column(name = "daycode")
    private Integer dayCode;

    @Column(name = "predicted_target")
    private Integer predictedTarget;
}
