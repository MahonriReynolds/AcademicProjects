

class Program
{
    static void Main(string[] args)
    {

        int width = Console.WindowWidth;
        int height = Console.WindowHeight;

        while (width < 75 || height < 20)
        {
            Console.Clear();
            Console.WriteLine("The game will not display properly in too small of a terminal.");
            Console.WriteLine($"Width must be at least 75. Currently {width}");
            Console.WriteLine($"Height must be at least 20. Currently {height}");
            Console.WriteLine("Resize terminal and hit enter to check size.");
            ConsoleKeyInfo keyInfo;
            do
            {
                keyInfo = Console.ReadKey(true);
            } while (keyInfo.Key != ConsoleKey.Enter);
            width = Console.WindowWidth;
            height = Console.WindowHeight;
        }
        
        width = (int)(width * 0.90);
        height = (int)(height * 0.90);
        Game game;
        do
        {
            game = new Game(width, height, seed: new Random().Next(-1000, 1000));
        }
        while (game.Run());
    }
}
