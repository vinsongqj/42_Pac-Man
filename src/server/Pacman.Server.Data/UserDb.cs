using Microsoft.EntityFrameworkCore;

namespace Pacman.Server.Data;

class PacmanDb(DbContextOptions<PacmanDb> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
}