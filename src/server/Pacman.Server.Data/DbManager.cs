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

    public async Task<bool> DeleteUserAsync(string name)
    {
        User? user = await GetUserAsync(name);
        if (user != null) 
        {
            _context.Users.Remove(user);
            await _context.SaveChangesAsync();
            return true;
        }
        return false;
    }

    public async Task<User?> GetUserAsync(string name)
    {
        return await _context.Users.FirstOrDefaultAsync(u => u.Name == name);
    }

    public async Task<List<User>> GetUsersByScoreAsync(int amount)
    {
        return await _context.Users.OrderByDescending(u => u.BestScore).Take(amount).ToListAsync();
    }

    public async Task CreateUserAsync(string name)
    {
        User user = new(name);
        await _context.Users.AddAsync(user);
    }

    public async Task<bool> UserExistsAsync(string name)
    {
        return await _context.Users.AnyAsync(u => u.Name == name);
    }
}