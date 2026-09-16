using System.Runtime.CompilerServices;
using Pacman.Server.Data;

namespace Pacman.Server.Core;

public class Orchestrator
{
    private readonly IDbManager _manager;

    public Orchestrator(IDbManager manager)
    {
        _manager = manager;
    }

    public async Task<List<UserDTO>> GetScoreboardAsync(int size)
    {
        List<User> users = await _manager.GetUsersByScoreAsync(size);
        return users.Select(u => UserDTO.FromUser(u)).ToList();
    }
}