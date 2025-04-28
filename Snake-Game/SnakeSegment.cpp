
#include "SnakeSegment.h"
#include <vector>

using namespace std;

SnakeSegment::SnakeSegment(vector<int> coords)
{
	this->_coords = coords;
}

void SnakeSegment::Advance(vector<int> coords)
{
	this->_coords = coords;
}

vector<int> SnakeSegment::GetCoords() const
{
	return this->_coords;
}
