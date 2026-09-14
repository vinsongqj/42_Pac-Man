using Pacman.Server.Data;

namespace Pacman.Server.Core;

public class Orchestrator
{
    private readonly IDbManager _manager;

    public Orchestrator(IDbManager manager)
    {
        _manager = manager;
    }
}