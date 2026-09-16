using Microsoft.OpenApi;
using Pacman.Server.Core;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
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

app.MapGet("/user", (Guid id, Orchestrator o) =>
{
    
});

app.MapPut("/user", (Guid id, int newScore, Orchestrator o) =>
{

});

app.MapPost("/signup", (string name, string password, Orchestrator o) =>
{

});

app.MapGet("/login", (string name, string password, Orchestrator o) =>
{

});

app.MapGet("/leaderboard", (int size, Orchestrator o) =>
{

});

app.Run();
