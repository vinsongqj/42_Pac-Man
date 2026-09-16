using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi;
using Pacman.Server.Core;
using Pacman.Server.Data;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
builder.Services.AddDbContext<PacmanDb>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection") ?? "Host=localhost;Database=pacman;Username=postgres;Password=postgres"));
builder.Services.AddScoped<IDbManager, DbManager>();
builder.Services.AddScoped<Orchestrator>();
builder.Services.AddSwaggerGen(options =>
{
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey
    });
    options.AddSecurityRequirement(doc => new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecuritySchemeReference("Bearer"),
            new List<string>()
        }
    });
});

var app = builder.Build();

app.UseHttpsRedirection();
app.UseSwagger();
app.UseSwaggerUI();

app.MapGet("/user", async (Guid id, Orchestrator o) =>
{
    
});

app.MapPut("/user", async (Guid id, int newScore, Orchestrator o) =>
{

});

app.MapPost("/signup", async (LoginRequest request, Orchestrator o) =>
{
    if (request.name.Length < 3)
        return Results.UnprocessableEntity("The name is too short, should be at least 3 chars.");
    if (request.password.Length < 4)
        return Results.UnprocessableEntity("The password is too short, should be at least 4 chars.");

    if (!await o.SignupAsync(request))
        return Results.Conflict("This name is already taken.");
    return Results.Ok("The user is successfully created.");
});

app.MapPost("/login", async (LoginRequest request, Orchestrator o) =>
{
    if (request.name.Length < 3)
        return Results.UnprocessableEntity("The name is too short, should be at least 3 chars.");
    if (request.password.Length < 4)
        return Results.UnprocessableEntity("The password is too short, should be at least 4 chars.");

    AuthDTO? auth = await o.LoginAsync(request);
    if (auth == null) return Results.Unauthorized();
    return Results.Ok(auth);
});

app.MapGet("/leaderboard", async (int size, Orchestrator o) =>
{
    if (size < 1) return Results.BadRequest("The size should not be less than 1.");

    List<UserDTO> leaderboard = await o.GetLeaderboardAsync(size);
    return Results.Ok(leaderboard);
});

app.Run();
