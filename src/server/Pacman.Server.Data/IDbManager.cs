namespace Pacman.Server.Data;

public interface IDbManager
{
    public Task SaveChangesAsync();

    public Task<User?> GetUserAsync(Guid id);

    public Task<List<User>> GetUsersByScoreAsync(int amount);

    public Task CreateUserAsync(string name, string password);
}