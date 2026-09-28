using Microsoft.EntityFrameworkCore;
using Pacman.Server.Core;
using Pacman.Server.Data;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
builder.Services.AddDbContext<PacmanDb>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection") ?? "Host=localhost;Database=pacman;Username=postgres;Password=postgres"));
builder.Services.AddScoped<IDbManager, DbManager>();
builder.Services.AddScoped<Orchestrator>();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseSwagger();
app.UseSwaggerUI();

app.MapPut("/user", async (string name, int newScore, Orchestrator o) =>
{
    if (name.Length <= 2) return Results.BadRequest("The name must be at least 3 chars long");
    if (newScore < 0) return Results.BadRequest("Score can not be negative");

    await o.EnsureUserCreated(name);
    await o.UpdateUserScore(name, newScore);
    return Results.Ok();
});

app.MapDelete("/user", async (string name, Orchestrator o) =>
{
    if (name.Length <= 2) return Results.BadRequest("The name must be at least 3 chars long");

    if (await o.DeleteUserAsync(name))
        return Results.NoContent();
    else
        return Results.BadRequest("User not found");
});

app.MapGet("/leaderboard", async (int size, Orchestrator o) =>
{
    if (size < 1) return Results.BadRequest("The size can not be less than 1.");

    List<UserDTO> leaderboard = await o.GetLeaderboardAsync(size);
    return Results.Ok(leaderboard);
});

app.Run();
