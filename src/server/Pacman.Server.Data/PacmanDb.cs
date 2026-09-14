using Microsoft.EntityFrameworkCore;

namespace Pacman.Server.Data;

public class PacmanDb(DbContextOptions<PacmanDb> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<User>()
            .HasIndex(u => u.Name)
            .IsUnique();

        modelBuilder.Entity<User>()
            .Property(u => u.Id)
            .ValueGeneratedNever();
    }
}