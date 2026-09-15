using Pacman.Server.Data;

public record UserDTO(string id, string name, int bestScore)
{
    string Id = id;
    string Name = name;
    int BestScore = bestScore;

    public UserDTO FromUser(User user)
    {
        return new UserDTO(user.Id.ToString(), user.Name, user.BestScore);
    }
}