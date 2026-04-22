package GolozoBackend.example.demo.predictionAI;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;


import java.time.LocalDate;
import java.util.List;

@Repository
public interface MatchRepository extends JpaRepository<Match, Long> {
    @Query("SELECT m FROM Match m WHERE m.date = " +
            "(SELECT MIN(m2.date) FROM Match m2 WHERE m2.team = m.team AND" +
            " m2.date >= :startDate AND m2.date <= :endDate) " +
            "AND m.venueCode = 1")
    List<Match> findUniqueTeamMatches(
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate);

    @Query("SELECT DISTINCT m.team FROM Match m")
    List<String> findAllDistinctTeams();

    @Query("SELECT m FROM Match m WHERE m.venueCode = 1")
    List<Match> getAllFixtures();

}

