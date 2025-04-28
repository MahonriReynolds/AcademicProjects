


public class MapMaker
{
    private Random _random;
    private int[] _table;
    private double _scaler;

    public MapMaker(int seed, double scaler=0.01, int tableSize=256)
    {
        _random = new Random(seed);
        this._table = new int [tableSize * 2];

        for (int i = 0; i < tableSize * 2; i++)
        {
            this._table[i] = i % tableSize;
        }

        for (int i = 0; i < tableSize; i++)
        {
            int j = _random.Next(tableSize);
            int temp = _table[i];
            _table[i] = _table[j];
            _table[j] = temp;
            _table[i + tableSize] = _table[i];
        }
        this._scaler = scaler;
    }

    private char WeightedRandom((char, float)[] weightedArray)
    {
        float totalWeight = weightedArray.Sum(item => item.Item2);
        float randomValue = (float)this._random.NextDouble() * totalWeight;

        foreach ((char character, float weight) in weightedArray)
        {
            randomValue -= weight;
            if (randomValue <= 0)
                return character;
        }

        return weightedArray.Last().Item1;
    }

    private (char, bool) NoiseToCell(double noise)
    {
        (char, float)[] water = [('_', 0.34f), (' ', 0.66f)];
        (char, float)[] sand = [('.', 0.15f), ('~', 0.35f), (',', 0.25f), (' ', 0.25f)];
        (char, float)[] forest = [('Ʌ', 0.20f), ('^', 0.20f), ('A', 0.10f), (',', 0.05f), (' ', 0.45f)];
        (char, float)[] plains = [('⌄', 0.05f), ('.', 0.025f), (' ', 0.925f)];
        
        if (noise < 0.25)
        {
            return (WeightedRandom(forest), false);   
        }
        else if (noise < 0.52)
        {
            return (WeightedRandom(plains), true);
        }
        else if (noise < 0.55)
        {
            return (WeightedRandom(sand), true);
        }
        else if (noise < 0.73)
        {   
            return (WeightedRandom(plains), true);
        }
        else if (noise < 0.74)
        {
            return (WeightedRandom(sand), true);
        }
        else
        {
            return (WeightedRandom(water), false);   
        }
    }

    private static double Fade(double t)
    {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    private static double Lerp(double t, double a, double b)
    {
        return a + t * (b - a);
    }

    private static double Grad(int hash, double x, double y)
    {
        int h = hash & 7;
        double u = h < 4 ? x : y;
        double v = h < 4 ? y : x;
        return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
    }

    private double GenerateNoise(double xf, double yf)
    {
        int X = (int)Math.Floor(xf) & 255;
        int Y = (int)Math.Floor(yf) & 255;

        int X1 = (X + 1) & 255;

        xf -= Math.Floor(xf);
        yf -= Math.Floor(yf);

        double u = Fade(xf);
        double v = Fade(yf);

        int A = this._table[X] + Y;
        int AA = this._table[A];
        int AB = this._table[A + 1];
        int B = this._table[X1] + Y;
        int BA = this._table[B];
        int BB = this._table[B + 1];

        AA %= 256;
        AB %= 256;
        BA %= 256;
        BB %= 256;

        double bottomLerp = Lerp(
            u, 
            Grad(this._table[AA], xf, yf), 
            Grad(this._table[BA], xf - 1, yf)
        );

        double topLerp = Lerp(
            u, 
            Grad(this._table[AB], xf, yf - 1), 
            Grad(this._table[BB], xf - 1, yf - 1)
        );

        double result = Lerp(v, bottomLerp, topLerp);

        return (result + 1) / 2;
    }

    public (char, bool) MakeCell(int x, int y)
    {
        return NoiseToCell(GenerateNoise(x * this._scaler, y * this._scaler));
    }
}

