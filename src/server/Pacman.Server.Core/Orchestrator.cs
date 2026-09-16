using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
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

    public async Task<bool> SignupAsync(LoginRequest request)
    {
        if (request.name.Length < 3) return false;
        if (request.password.Length < 4) return false;
        if (await _manager.UserExistsAsync(request.name)) return false;
        
        string encryptedPassword = BCrypt.Net.BCrypt.EnhancedHashPassword(request.Password);
        await _manager.CreateUserAsync(request.name, encryptedPassword);
        await _manager.SaveChangesAsync();
        return true;
    }

    public async Task<AuthDTO?> LoginAsync(LoginRequest request)
    {
        //todo: add JWT
        User? user = await _manager.GetUserAsync(request.name);
        if (user == null) return null;
        if (!BCrypt.Net.BCrypt.EnhancedVerify(request.Password, user.Password)) return null;

        string key = "very_damn_long_key_that_should_not_be_hardcoded_but_i_dont_care_yet";
        var tokenHandler = new JwtSecurityTokenHandler();
        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity([
                new Claim(ClaimTypes.Name, user.Name),
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString())
            ]),
            Expires = DateTime.UtcNow.AddDays(7),
            Issuer = "PacmanDatabase",
            SigningCredentials = new SigningCredentials(
                new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key)),
                SecurityAlgorithms.HmacSha256)
        };
        var token = tokenHandler.CreateToken(tokenDescriptor);
        var tokenString = tokenHandler.WriteToken(token);
        return new AuthDTO(tokenString);
    }
}