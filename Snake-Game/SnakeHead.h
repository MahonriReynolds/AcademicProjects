
#pragma once
#include <vector>

using namespace std;

class SnakeHead
{
private:
	vector<int> _coords;
	vector<int> _step;

public:

	SnakeHead(vector<int> coords);

	void Advance(vector<int> step);
	vector<int> GetCoords() const;
};

