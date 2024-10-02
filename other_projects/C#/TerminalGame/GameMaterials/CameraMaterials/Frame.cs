

public class Frame
{
    private char[,] _contentArray;

    public Frame(int width, int height)
    {
        this._contentArray = new char[width, height];
    }

    public void UpdateCell(int[] coords, char content)
    {
        this._contentArray[coords[0], coords[1]] = content;
    }

    public void Fill(char[,] fillContent)
    {
        this._contentArray = fillContent;
    }

    public char[,] GetContent()
    {
        return this._contentArray;
    }
}

