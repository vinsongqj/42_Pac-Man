using Pacman.Server.Data;
using BCrypt.Net;

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

    public async Task<bool> SignupAsync(LoginRequest request)
    {
        if (request.name.Length < 3) return false;
        if (request.password.Length < 4) return false;
        if (await _manager.UserExistsAsync(request.name)) return false;
        
        string encryptedPassword = BCrypt.Net.BCrypt.EnhancedHashPassword(request.Password);
        await _manager.CreateUserAsync(request.name, encryptedPassword);
        return true;
    }

    public async Task<bool> LoginAsync(LoginRequest request)
    {
        //todo: add JWT
        User? user = await _manager.GetUserAsync(request.name);
        if (user == null) return false;
        if (BCrypt.Net.BCrypt.EnhancedVerify(request.Password, user.Password)) return false;
        return true;
    }
}