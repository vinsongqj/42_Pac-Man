using Microsoft.EntityFrameworkCore;

namespace Pacman.Server.Data;

class PacmanDb(DbContextOptions<PacmanDb> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<User>()
            .HasIndex(p => p.Name)
            .IsUnique();
    }
}