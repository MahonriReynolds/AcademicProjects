
public class EntityMesh
{
    private PlayerO _player;
    private List<Enemy> _enemies;
    private Type[] _enemyTypes;
    private Random _random;

    public EntityMesh(PlayerO player)
    {
        this._player = player;
        this._enemies = [];
        this._enemyTypes = [
                typeof(EnemyX), typeof(EnemyX), typeof(EnemyX), typeof(EnemyX), typeof(EnemyX),
                typeof(EnemyH),
                typeof(EnemyI),
                typeof(EnemyW)
            ];
        this._random = new Random();
    }

    public void AddEnemy(int[] center, bool[,] pathways)
    {
        List<Tuple<int, int>> validPositions = [];

        int rows = pathways.GetLength(0);
        int cols = pathways.GetLength(1);

        for (int j = 0; j < cols; j++)
        {
            if (pathways[0, j])
            {
                validPositions.Add(Tuple.Create(0, j));
            }
            if (pathways[rows - 1, j])
            {
                validPositions.Add(Tuple.Create(rows - 1, j));
            }
        }

        for (int i = 0; i < rows; i++)
        {
            if (pathways[i, 0])
            {
                validPositions.Add(Tuple.Create(i, 0));
            }
            if (pathways[i, cols - 1])
            {
                validPositions.Add(Tuple.Create(i, cols - 1));
            }
        }

        if (validPositions.Count > 0)
        {
            int randomIndex = this._random.Next(0, validPositions.Count);
            Tuple<int, int> selectedPosition = validPositions[randomIndex];
            int selectedRow = selectedPosition.Item1;
            int selectedCol = selectedPosition.Item2;

            int adjustedRow = center[0] - (rows / 2) + selectedRow;
            int adjustedCol = center[1] - (cols / 2) + selectedCol;

            Type enemyType = this._enemyTypes[this._random.Next(this._enemyTypes.Length)];
            Enemy newEnemy = (Enemy)Activator.CreateInstance(enemyType, adjustedRow, adjustedCol, this._player);

            this._enemies.Add(newEnemy);
        }
    }

    public bool CheckValidCenter(bool[,] pathways)
    {
        int initX = pathways.GetLength(0) / 2;
        int initY = pathways.GetLength(1) / 2;

        return pathways[initX, initY];
    }

    public void AdvanceEnemies(int[] center, bool[,] pathways)
    {
        int offsetX = pathways.GetLength(0) / 2;
        int offsetY = pathways.GetLength(1) / 2;

        List<Enemy> enemiesToRemove = [];

        foreach (Enemy enemy in this._enemies)
        {
            enemy.Decay();
            if (enemy.GetHealthPercentage() <= 0)
            {
                enemiesToRemove.Add(enemy);
            }
            
            enemy.Follow();

            int[] enemyCoords = enemy.Locate();
            int enemyX = enemyCoords[0] - (center[0] - offsetX);
            int enemyY = enemyCoords[1] - (center[1] - offsetY);

            foreach (Enemy otherEnemy in this._enemies)
            {
                if (enemy != otherEnemy)
                {
                    int[] otherEnemyCoords = otherEnemy.Locate();
                    int otherEnemyX = otherEnemyCoords[0] - (center[0] - offsetX);
                    int otherEnemyY = otherEnemyCoords[1] - (center[1] - offsetY);

                    if (enemyX == otherEnemyX && enemyY == otherEnemyY)
                    {
                        enemy.BackStep();
                    }
                }
                if (enemyX >= 0 && enemyX < pathways.GetLength(0) &&
                    enemyY >= 0 && enemyY < pathways.GetLength(1))
                {
                    if (!pathways[enemyX, enemyY])
                    {
                        enemiesToRemove.Add(enemy);
                    }
                }
            }
        }
        foreach (Enemy enemyToRemove in enemiesToRemove)
        {
            this._enemies.Remove(enemyToRemove);
        }
    }

    public void HandleCollisions(int[] center, bool[,] pathways)
    {
        int offsetX = pathways.GetLength(0) / 2;
        int offsetY = pathways.GetLength(1) / 2;
        int[] playerCoords = this._player.Locate();
        int playerX = playerCoords[0] - (center[0] - offsetX);
        int playerY = playerCoords[1] - (center[1] - offsetY);

        if (!pathways[playerX, playerY])
        {
            this._player.BackStep();
            playerCoords = this._player.Locate();
        }

        foreach (Enemy enemy in this._enemies)
        {
            int[] enemyCoords = enemy.Locate();

            if (playerCoords[0] == enemyCoords[0] && playerCoords[1] == enemyCoords[1])
            {
                this._player.TakeDamage(enemy.GetAttack());
                enemy.BackStep();
                enemy.BackStep();
            }
        }
    }

    public char[,] GetSelection(int[] center, int width, int height)
    {
        char[,] selection = new char[width, height];
        int[] playerPos = this._player.Locate();

        int offsetX = width / 2;
        int offsetY = height / 2;
        int playerX = playerPos[0] - (center[0] - offsetX);
        int playerY = playerPos[1] - (center[1] - offsetY);

        selection[playerX, playerY] = $"{this._player}"[0];

        foreach (Enemy enemy in this._enemies)
        {
            int[] enemyPos = enemy.Locate();

            int enemyX = enemyPos[0] - (center[0] - offsetX);
            int enemyY = enemyPos[1] - (center[1] - offsetY);

            if (enemyX >= 0 && enemyX < width && enemyY >= 0 && enemyY < height)
            {
                selection[enemyX, enemyY] = $"{enemy}"[0]; 
            }
        }

        return selection;
    }
}


