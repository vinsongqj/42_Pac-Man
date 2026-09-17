using Microsoft.EntityFrameworkCore;

namespace Pacman.Server.Data;

public class DbManager : IDbManager
{
    private readonly PacmanDb _context;

    public DbManager(PacmanDb context) => _context = context;

    public async Task SaveChangesAsync()
    {
        await _context.SaveChangesAsync();
    }

    public async Task<User?> GetUserAsync(Guid id)
    {
        return await _context.Users.FirstOrDefaultAsync(u => u.Id == id);
    }

    public async Task<User?> GetUserAsync(string name)
    {
        return await _context.Users.FirstOrDefaultAsync(u => u.Name == name);
    }

    public async Task<List<User>> GetUsersByScoreAsync(int amount)
    {
        return await _context.Users.OrderBy(u => u.BestScore).Take(amount).ToListAsync();
    }

    public async Task CreateUserAsync(string name, string password)
    {
        User user = new(name, password);
        await _context.Users.AddAsync(user);
    }

    public async Task<bool> UserExistsAsync(string name)
    {
        return await _context.Users.AnyAsync(u => u.Name == name);
    }
}