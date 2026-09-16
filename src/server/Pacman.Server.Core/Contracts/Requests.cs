namespace Pacman.Server.Core;

public record LoginRequest(string name, string password)
{
    public string Name = name;
    public string Password = password;
}

public record UpdateBestScoreRequest(int newScore)
{
    public int NewScore = newScore;
}