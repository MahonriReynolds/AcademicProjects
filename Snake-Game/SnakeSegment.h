
#pragma once
#include <vector>

using namespace std;

class SnakeSegment
{
private:
	vector<int> _coords;

public:

	SnakeSegment(vector<int> coords);

	void Advance(vector<int> coords);
	vector<int> GetCoords() const;
};

