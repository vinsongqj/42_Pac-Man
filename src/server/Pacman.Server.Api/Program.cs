using Microsoft.OpenApi;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();
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

app.MapGet("/user", (Guid id) =>
{
    
});

app.MapPut("/user", (Guid id, int newScore) =>
{

});

app.MapPost("/signup", (string name, string password) =>
{

});

app.MapGet("/login", (string name, string password) =>
{

});

app.MapGet("/leaderboard", (int size) =>
{

});

app.Run();
