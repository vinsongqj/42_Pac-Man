using Pacman.Server.Data;

namespace Pacman.Server.Core;

public class Orchestrator
{
    private readonly IDbManager _manager;

    public Orchestrator(IDbManager manager)
    {
        _manager = manager;
    }

    public async Task<List<UserDTO>> GetLeaderboardAsync(int size)
    {
        List<User> users = await _manager.GetUsersByScoreAsync(size);
        return users.Select(u => UserDTO.FromUser(u)).ToList();
    }

    public async Task<bool> UpdateUserScore(string name, int score)
    {
        User? user = await _manager.GetUserAsync(name);
        if (user != null)
        {
            if (user.TryUpdateBestScore(score))
            {
                await _manager.SaveChangesAsync();
                return true;
            }
        }
        return false;
    }

    public async Task EnsureUserCreated(string name)
    {
        if (!await _manager.UserExistsAsync(name))
        {
            await _manager.CreateUserAsync(name);
            await _manager.SaveChangesAsync();
        }
    }
}