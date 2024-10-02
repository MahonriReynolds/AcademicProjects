
#include "SnakeHead.h"
#include <vector>

using namespace std;

SnakeHead::SnakeHead(vector<int> coords)
{
	this->_coords = coords;
	this->_step = {0, 0};
}

void SnakeHead::Advance(vector<int> step)
{
	if (!step.empty())
	{
		this->_step = step;
	}
	
	for (int i = 0; i < this->_coords.size(); i++)
	{
		this->_coords[i] = this->_coords[i] + this->_step[i];
	}
}

vector<int> SnakeHead::GetCoords() const
{
	return this->_coords;
}
