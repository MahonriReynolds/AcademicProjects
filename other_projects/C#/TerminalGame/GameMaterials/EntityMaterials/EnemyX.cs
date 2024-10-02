

public class EnemyX:Enemy
{
    public EnemyX(int x, int y, PlayerO player)
    : base (x, y, 'X', 2, player)
    { 
    }

    public override void Decay()
    {
        this._health -= 0.1f;
        if (this._health > this._maxHealth)
        {
            this._health = this._maxHealth;
        }
    }

    public override void Follow()
    {
        int[] currentCoords = this.Locate();
        int[] targetCoords = this._targetPlayer.Locate();

        int[] difference = [targetCoords[0] - currentCoords[0], targetCoords[1] - currentCoords[1]];

        int[] step = [0, 0];

        List<int> validDirections = new List<int>();
        if (difference[0] != 0)
        {
            validDirections.Add(0);
        }
        if (difference[1] != 0)
        {
            validDirections.Add(1);
        }

        if (validDirections.Count > 0)
        {
            Random random = new Random();
            int directionIndex = random.Next(validDirections.Count);
            int direction = validDirections[directionIndex];

            if (direction == 0)
            {
                step[0] = Math.Sign(difference[0]);
            }
            else if (direction == 1)
            {
                step[1] = Math.Sign(difference[1]);
            }
        }

        base.Advance(step);
    }
}



