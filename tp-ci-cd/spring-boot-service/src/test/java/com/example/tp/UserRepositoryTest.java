package com.example.tp;

import com.example.tp.model.User;
import com.example.tp.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.mongo.DataMongoTest;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.TestPropertySource;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DataMongoTest
@TestPropertySource(properties = "spring.mongodb.embedded.version=4.4.0")
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
public class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    public void testSaveAndFindUser() {
        // Given
        User user = new User("Test User " + System.currentTimeMillis(), "test@example.com");
        
        // When
        User savedUser = userRepository.save(user);
        List<User> users = userRepository.findAll();
        
        // Then - Vérifiez que l'utilisateur sauvegardé est dans la liste
        assertNotNull(savedUser.getId());
        assertFalse(users.isEmpty());
        
        // Trouvez l'utilisateur par son ID plutôt que par position
        User foundUser = users.stream()
            .filter(u -> u.getId().equals(savedUser.getId()))
            .findFirst()
            .orElse(null);
        
        assertNotNull(foundUser);
        assertEquals(savedUser.getName(), foundUser.getName());
    }

    @Test
    public void testFindByName() {
        // Given
        User user = new User("John", "john@example.com");
        userRepository.save(user);
        
        // When
        List<User> foundUsers = userRepository.findByName("John");
        
        // Then
        assertFalse(foundUsers.isEmpty());
        assertEquals("John", foundUsers.get(0).getName());
    }
}