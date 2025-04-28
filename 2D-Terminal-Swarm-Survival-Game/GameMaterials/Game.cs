
using System.Diagnostics;
public class Game
{
    private Map _map;
    private Camera _camera;
    private PlayerO _player;
    private Controller _controller;
    private EntityMesh _mesh;
    private int _width;
    private int _height;
    private Stopwatch _stopwatch;
    private float _lastAddEnemy;
    private float _lastAdvanceEnemies;
    private int[] _centerPos;

    public Game(int width, int height, int seed)
    {
        height -= 5;
        this._map = new Map(seed, width, height);
        this._camera = new Camera(width, height);
        this._player = new PlayerO(1, 0, 100, 50);
        this._controller = new Controller();
        this._mesh = new EntityMesh(this._player);
        this._width = width;
        this._height = height;
    }

    private bool IsElapsed(float lastTriggeredTime, float intervalSeconds)
    {
        return (this._stopwatch.Elapsed.TotalSeconds - lastTriggeredTime) >= intervalSeconds;
    }

    private void SetUp()
    {
        this._lastAddEnemy = 0;
        this._lastAdvanceEnemies = 0;
        this._stopwatch = Stopwatch.StartNew();
        Console.Clear();

        int[] playerPos;
        (char[,], bool[,]) mapSelection;
        do
        {
            this._player.Advance([-1, 0]);
            playerPos = this._player.Locate();
            this._map.Extend(playerPos, this._width, this._height, [-1, 0]);
            mapSelection = this._map.GetSelection(playerPos, this._width, this._height);

        }while (!this._mesh.CheckValidCenter(mapSelection.Item2));

        this._centerPos = this._player.Locate();
    }

    private int Iterate()
    {
        (int[], int) input = this._controller.GetStep();
        int[] step = input.Item1;
        if (step[0] != 0 || step[1] != 0)
        {
            this._player.Advance(step);
        }
        else
        {
            this._player.Rest();
        }
        
        int[] playerPos = this._player.Locate();

        int xPosDelta = Math.Abs(playerPos[0] - this._centerPos[0]);
        int yPosDelta = Math.Abs(playerPos[1] - this._centerPos[1]);

        if (xPosDelta > this._width / 10 || yPosDelta > this._height / 10)
        {
            this._centerPos[0] += step[0];
            this._centerPos[1] += step[1];
        }
        this._map.Extend(this._centerPos, this._width, this._height, step);
        
        (char[,], bool[,]) mapSelection = this._map.GetSelection(this._centerPos, this._width, this._height);

        if (IsElapsed(this._lastAddEnemy, (float)(1 / this._stopwatch.Elapsed.TotalSeconds)))
        {
            this._mesh.AddEnemy(this._centerPos, mapSelection.Item2);
            this._lastAddEnemy = (float)this._stopwatch.Elapsed.TotalSeconds;
        }

        if (IsElapsed(this._lastAdvanceEnemies, 0.25f))
        {
            this._mesh.AdvanceEnemies(this._centerPos, mapSelection.Item2);
            this._lastAdvanceEnemies = (float)this._stopwatch.Elapsed.TotalSeconds;
        }

        this._mesh.HandleCollisions(this._centerPos, mapSelection.Item2);

        this._camera.MakeNextFrame(
            mapSelection.Item1,
            this._mesh.GetSelection(this._centerPos, this._width, this._height)
        );

        float playerHealth = this._player.GetHealthPercentage();

        this._camera.Display(
            $"Countdown: {(int)(60 - this._stopwatch.Elapsed.TotalSeconds)}\n" +
            $"({playerPos[0]}, {playerPos[1]})\n" +
            $"Health:  {(int)(playerHealth * 100)}%\n" +
            $"Stamina: {(int)(this._player.GetStaminaPercentage() * 100)}%" 
        );
        
        if (playerHealth <= 0)
        {
            return 2;
        }
        else if (this._stopwatch.Elapsed.TotalSeconds > 60)
        {
            return 3;
        }
        return input.Item2;
    }

    public bool Run()
    {
        Menu mainMenu = new Menu(
            @"
             __  __       _            __  __                  
            |  \/  | __ _(_)_ __      |  \/  | ___ _ __  _   _ 
            | |\/| |/ _` | | '_ \     | |\/| |/ _ \ '_ \| | | |
            | |  | | (_| | | | | |    | |  | |  __/ | | | |_| |
            |_|  |_|\__,_|_|_| |_|    |_|  |_|\___|_| |_|\__,_|
            ", 
            ["New Game", "Instructions", "Quit"]
        );

        Menu pauseMenu = new Menu(
            @"
             ____                           __  __                  
            |  _ \ __ _ _   _ ___  ___     |  \/  | ___ _ __  _   _ 
            | |_) / _` | | | / __|/ _ \    | |\/| |/ _ \ '_ \| | | |
            |  __/ (_| | |_| \__ \  __/    | |  | |  __/ | | | |_| |
            |_|   \__,_|\__,_|___/\___|    |_|  |_|\___|_| |_|\__,_|
            ", 
            ["Resume", "Main Menu"]
        );

        bool isRunning = false;
        int choice;
        do
        {
            choice = mainMenu.Display();
            if (choice == 0)
            {
                isRunning = true;
                this.SetUp();
            }
            else if (choice == 1)
            {
                Console.Clear();
                Console.WriteLine(
                    @"
             ___           _                   _   _                 
            |_ _|_ __  ___| |_ _ __ _   _  ___| |_(_) ___  _ __  ___ 
             | || '_ \/ __| __| '__| | | |/ __| __| |/ _ \| '_ \/ __|
             | || | | \__ \ |_| |  | |_| | (__| |_| | (_) | | | \__ \
            |___|_| |_|___/\__|_|   \__,_|\___|\__|_|\___/|_| |_|___/
                    
                          
         * Navigate with ↑ ↓ ← →   
         * Pause with Esc

         * Survive for 1 minute
         ** Rest if you need to
         ** Enemies have a set lifespan
         ** Enemies get lost in lakes and forests
         ** Pathways lead you between lakes and forests
                
         * Close this page with Enter       
                    "
                );
                ConsoleKeyInfo keyInfo;
                do
                {
                    keyInfo = Console.ReadKey(true);
                } while (keyInfo.Key != ConsoleKey.Enter);
            }
            else if (choice == 2)
            {
                return false;
            }

        }while(choice == 1);

        int iterationCode;

        while (isRunning)
        {
            iterationCode = this.Iterate();
            if (iterationCode == 1)
            {
                this._stopwatch.Stop();
                if (pauseMenu.Display() == 1)
                {
                    return true;
                }
                this._camera.RecoverFrame();
                this._stopwatch.Start();
            }
            else if (iterationCode == 2)
            {
                Console.Clear();
                Console.WriteLine(
                    @"
                 ____  _                            ____  _          _ 
                |  _ \| | __ _ _   _  ___ _ __     |  _ \(_) ___  __| |
                | |_) | |/ _` | | | |/ _ \ '__|    | | | | |/ _ \/ _` |
                |  __/| | (_| | |_| |  __/ |       | |_| | |  __/ (_| |
                |_|   |_|\__,_|\__, |\___|_|       |____/|_|\___|\__,_|
                               |___/                                   
                                                      
        
         You died
         Press enter to return to the main menu  
                    "
                );
                ConsoleKeyInfo keyInfo;
                do
                {
                    keyInfo = Console.ReadKey(true);
                } while (keyInfo.Key != ConsoleKey.Enter);
                return true;
            }
            else if (iterationCode == 3)
            {
                Console.Clear();
                Console.WriteLine(
                    @"
                 _____ _                _          _   _       
                |_   _(_)_ __ ___   ___( )___     | | | |_ __  
                  | | | | '_ ` _ \ / _ \// __|    | | | | '_ \ 
                  | | | | | | | | |  __/ \__ \    | |_| | |_) |
                  |_| |_|_| |_| |_|\___| |___/     \___/| .__/ 
                                                        |_|    
                    
        
         You survived
         Press enter to return to the main menu  
                    "
                );
                ConsoleKeyInfo keyInfo;
                do
                {
                    keyInfo = Console.ReadKey(true);
                } while (keyInfo.Key != ConsoleKey.Enter);
                return true;
            }
            Thread.Sleep(30);
        }
        return false;
    }
}


