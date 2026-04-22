package GolozoBackend.example.demo.predictionAI;
import org.apache.poi.sl.usermodel.SlideShow;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class MatchService {


    @Autowired
    private MatchRepository matchRepository;

    public List<Match> getPredictionMatches() {
        LocalDate startDate = LocalDate.now();
        LocalDate endDate =  startDate.plusWeeks(1);
        List<Match> matches = matchRepository.findUniqueTeamMatches(startDate, endDate);

        if (matches.isEmpty()) {
            System.out.println("No matches found");
        }

        return matches;
    }

    public List<String> getAllTeams(){
        return matchRepository.findAllDistinctTeams();
    }

    public List<Match> getAllFixtures(){
        return matchRepository.getAllFixtures();
    }




}
