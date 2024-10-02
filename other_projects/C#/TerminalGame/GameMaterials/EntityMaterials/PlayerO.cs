

public class PlayerO:Entity
{
    private int _maxStamina;
    private float _stamina;

    public PlayerO(int x, int y, int maxHealth, int _maxStamina)
    : base (x, y, maxHealth, 'O')
    {
        this._maxStamina = _maxStamina;
        this._stamina = _maxStamina;
    }

    public float GetStaminaPercentage()
    {
        return this._stamina / this._maxStamina;
    }

    public void Rest()
    {
        this._health += 0.01f;
        if (this._health > this._maxHealth)
        {
            this._health = this._maxHealth;
        }
        
        this._stamina += this._maxStamina * 0.0005f;
        if (this._stamina > this._maxStamina)
        {
            this._stamina = this._maxStamina;
        }
    }

    public override void Advance(int[] step)
    {
        if (this._stamina > 0)
        {
            base.Advance(step);
            this._stamina -= this._maxStamina * 0.001f;
        }
    }

    public override void BackStep()
    {
        base.BackStep();
        this._stamina -= this._maxStamina * 0.001f;
        if (this._stamina < 0)
        {
            this._stamina = 0;
        }
    }
}

