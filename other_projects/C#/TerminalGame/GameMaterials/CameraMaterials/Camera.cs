
public class Camera
{
    private Frame _frame1;
    private Frame _frame2;
    private Dictionary<char, ConsoleColor> _colorCode;

    public Camera(int viewWidth, int viewHeight)
    {
        this._frame1 = new Frame(viewWidth, viewHeight);
        this._frame2 = new Frame(viewWidth, viewHeight);

        this._colorCode = new Dictionary<char, ConsoleColor>()
        {
            {'⌄', ConsoleColor.Green},
            {'.', ConsoleColor.Green},
            {'Ʌ', ConsoleColor.DarkGreen},
            {'A', ConsoleColor.DarkGreen},
            {'^', ConsoleColor.DarkGreen},
            {'_', ConsoleColor.DarkCyan},
            {'~', ConsoleColor.DarkGray},
            {',', ConsoleColor.DarkGray},
            {'O', ConsoleColor.DarkMagenta},
            {'X', ConsoleColor.DarkRed},
            {'W', ConsoleColor.DarkRed},
            {'I', ConsoleColor.DarkRed},
            {'H', ConsoleColor.DarkRed}
        };
    }

    public void MakeNextFrame(char[,] mapContent, char[,] meshContent)
    {
        this._frame2.Fill(mapContent);

        for (int i = 0; i < mapContent.GetLength(0); i++)
        {
            for (int j = 0; j < mapContent.GetLength(1); j++)
            {
                if (meshContent[i, j] != '\0')
                {
                    this._frame2.UpdateCell([i, j], meshContent[i, j]);
                }
            }
        }
    }

    public void RecoverFrame()
    {
        char[,] frame1Data = this._frame1.GetContent();
        int height = frame1Data.GetLength(1);
        int width = frame1Data.GetLength(0);

        Console.CursorVisible = false;
        for (int i = 0; i < width; i++)
        {
            for (int j = 0; j < height; j++)
            {
                Console.SetCursorPosition(i, j);

                if (this._colorCode.ContainsKey(frame1Data[i, j]))
                {
                    Console.ForegroundColor = this._colorCode[frame1Data[i, j]];
                }
                else
                {
                    Console.ResetColor();
                }            
                Console.Write(frame1Data[i, j]);
            }
        }
        Console.ResetColor();
    }

    public void Display(string stats)
    {
        char[,] frame1Data = this._frame1.GetContent();
        char[,] frame2Data = this._frame2.GetContent();

        int height = frame1Data.GetLength(1);
        int width = frame1Data.GetLength(0);

        Console.CursorVisible = false;
        for (int i = 0; i < width; i++)
        {
            for (int j = 0; j < height; j++)
            {
                if (frame1Data[i, j] != frame2Data[i, j])
                {
                    this._frame1.UpdateCell([i, j], frame2Data[i, j]);
                    Console.SetCursorPosition(i, j);

                    if (this._colorCode.ContainsKey(frame2Data[i, j]))
                    {
                        Console.ForegroundColor = this._colorCode[frame2Data[i, j]];
                    }
                    else
                    {
                        Console.ResetColor();
                    }            
                    Console.Write(frame2Data[i, j]);
                }
            } 
        }
        Console.ResetColor();
        for(int i = 0; i < width; i++)
        {
            Console.SetCursorPosition(i, height);
            Console.Write(' ');
            Console.SetCursorPosition(i, height + 1);
            Console.Write(' ');
            Console.SetCursorPosition(i, height + 2);
            Console.Write(' ');
            Console.SetCursorPosition(i, height + 3);
            Console.Write(' ');
        }
        Console.SetCursorPosition(0, height);
        Console.WriteLine(stats);
    }
}



