
public class Map
{
    private Dictionary<(int, int), (char, bool)> _mapContent;
    private MapMaker _mapMaker;

    public Map(int seed, int initWidth, int initHeight)
    {
        this._mapContent = new Dictionary<(int, int), (char, bool)>();
        int startX = -(initWidth / 2);
        int startY = -(initHeight / 2);
        this._mapMaker = new MapMaker(seed);

        for (int x = 0; x < initWidth; x++)
        {
            int mapX = startX + x;
            for (int y = 0; y < initHeight; y++)
            {
                int mapY = startY + y;
                this._mapContent[(mapX, mapY)] = this._mapMaker.MakeCell(mapX, mapY);
            }
        }
    }

    public void Extend(int[] center, int width, int height, int[] step)
    {
        int startX = center[0] - width / 2;
        int startY = center[1] - height / 2;

        int stepX = step[0];
        int stepY = step[1];

        if (Math.Abs(stepX) == 1)
        {
            int mapX = startX + (stepX == 1 ? width - 1 : 0);

            for (int y = 0; y < height; y++)
            {
                int mapY = startY + y;
                if (!this._mapContent.ContainsKey((mapX, mapY)))
                {
                    this._mapContent[(mapX, mapY)] = this._mapMaker.MakeCell(mapX, mapY);
                }
            }
        }

        else if (Math.Abs(stepY) == 1)
        {
            int mapY = startY + (stepY == 1 ? height - 1 : 0);

            for (int x = 0; x < width; x++)
            {
                int mapX = startX + x;
                if (!this._mapContent.ContainsKey((mapX, mapY)))
                {
                    this._mapContent[(mapX, mapY)] = this._mapMaker.MakeCell(mapX, mapY);
                }
            }
        }
    }

    public (char[,], bool[,]) GetSelection(int[] center, int width, int height)
    {
        char[,] selection = new char[width, height];
        bool[,] pathways = new bool[width, height];
        int startX = center[0] - width / 2;
        int startY = center[1] - height / 2;

        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                int mapX = startX + x;
                int mapY = startY + y;
                selection[x, y] = this._mapContent[(mapX, mapY)].Item1;
                pathways[x, y] = this._mapContent[(mapX, mapY)].Item2;
            }
        }
        
        return (selection, pathways);
    }
}


