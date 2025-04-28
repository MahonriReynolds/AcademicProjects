#pragma once

#include "SnakeHead.h"
#include "SnakeSegment.h"

#include <memory>
#include <vector>
#include <list>

using namespace std;

class Snake
{
private:
	shared_ptr<SnakeHead> _head;
	list<shared_ptr<SnakeSegment>> _segments;
	
public:

	Snake(vector<int> start);

	vector<int> Advance(vector<int> step = {});
	void Grow(vector<int> step);
	vector < vector<int>> Points();
};

