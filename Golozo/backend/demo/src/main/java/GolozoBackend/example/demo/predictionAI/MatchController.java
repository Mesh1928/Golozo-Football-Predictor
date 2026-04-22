package GolozoBackend.example.demo.predictionAI;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class MatchController {

    private final MatchService matchService;

    @Autowired
    public MatchController(MatchService matchService) {
        this.matchService = matchService;
    }

    @GetMapping("/matches/future-fixtures")
    public List<Match> getMatches() {
        return matchService.getPredictionMatches();
    }

    @GetMapping("/matches/teams")
    public List<String> getTeams(){
        return matchService.getAllTeams();
    }

    @GetMapping("/matches/allFixtures")
    public List<Match> getAllMatches(){
        return matchService.getAllFixtures();
    }


}
