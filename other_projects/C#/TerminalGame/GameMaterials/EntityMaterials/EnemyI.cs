

public class EnemyI:Enemy
{
    public EnemyI(int x, int y, PlayerO player)
    : base (x, y, 'I', 1, player)
    {
    }

    public override void Decay()
    {
        this._health -= 0.3f;
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

        if (difference[0] != 0 && difference[1] != 0)
        {
            step[0] = Math.Sign(difference[0]);
            step[1] = Math.Sign(difference[1]);
        }
        else
        {
            if (difference[0] != 0)
            {
                step[0] = Math.Sign(difference[0]);
            }
            if (difference[1] != 0)
            {
                step[1] = Math.Sign(difference[1]);
            }
        }

        base.Advance(step);
    }

}



