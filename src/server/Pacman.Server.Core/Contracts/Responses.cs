using Pacman.Server.Data;

namespace Pacman.Server.Core;

public record UserDTO(string id, string name, int bestScore)
{
    string Id = id;
    string Name = name;
    int BestScore = bestScore;

    public static UserDTO FromUser(User user)
    {
        return new UserDTO(user.Id.ToString(), user.Name, user.BestScore);
    }
}