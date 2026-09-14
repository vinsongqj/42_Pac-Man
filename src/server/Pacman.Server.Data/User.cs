class User
{
    public Guid     Id {get; private set;}
    public string   Name {get; private set;} = null!;
    public string   Password {get; private set;} = null!;
    public int      BestScore {get; private set;}

    public bool TryUpdateBestScore(int newScore)
    {
        if (newScore < BestScore) return false;
        BestScore = newScore;
        return true;
    }
}