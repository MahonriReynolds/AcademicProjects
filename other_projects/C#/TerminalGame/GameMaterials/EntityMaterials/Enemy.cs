

public abstract class Enemy:Entity
{
    protected PlayerO _targetPlayer;
    private float _attack;

    public Enemy(int x, int y, char model, float attack, PlayerO player)
    : base (x, y, 3, model)
    {
        this._targetPlayer = player;
        this._attack = attack;
    }

    public abstract void Decay();

    public float GetAttack()
    {
        return this._attack;
    }

    public abstract void Follow();
}



