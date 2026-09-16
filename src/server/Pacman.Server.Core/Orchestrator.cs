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

    public async Task<bool> Signup(LoginRequest request)
    {
        //todo: add encrypting
        if (request.name.Length < 3) return false;
        if (request.password.Length < 4) return false;
        if (await _manager.UserExistsAsync(request.name)) return false;
        await _manager.CreateUserAsync(request.name, request.password);
        return true;
    }

    public async Task<bool> Login(LoginRequest request)
    {
        //todo: add JWT
        User? user = await _manager.GetUserAsync(request.name);
        if (user == null) return false;
        if (user.Password != request.Password) return false;
        return true;
    }
}