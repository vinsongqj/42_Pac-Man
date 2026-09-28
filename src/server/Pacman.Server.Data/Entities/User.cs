namespace Pacman.Server.Data;

public class User(string name)
{
    public Guid     Id {get; private set;} = Guid.NewGuid();
    public string   Name {get; private set;} = name;
    public int      BestScore {get; private set;} = 0;

    public bool TryUpdateBestScore(int newScore)
    {
        if (newScore < BestScore) return false;
        BestScore = newScore;
        return true;
    }
}