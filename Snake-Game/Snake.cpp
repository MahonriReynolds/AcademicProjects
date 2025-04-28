
#include "Snake.h"
#include "SnakeHead.h"
#include "SnakeSegment.h"

#include <memory>
#include <vector>
#include <list>

using namespace std;

Snake::Snake(vector<int> start)
{
	shared_ptr<SnakeHead> newHead;
	newHead = make_shared<SnakeHead>(SnakeHead(start));
	this->_head = newHead;

	this->_segments = {};
}

vector<int> Snake::Advance(vector<int> step)
{
	vector<int> prevCoords;

	prevCoords = this->_head->GetCoords();

	this->_head->Advance(step);

	for (shared_ptr<SnakeSegment> segment : this->_segments)
	{
		vector<int> tmpCoords;
		tmpCoords = segment->GetCoords();

		segment->Advance(prevCoords);

		prevCoords = tmpCoords;
	}
	return prevCoords;
}

void Snake::Grow(vector<int> step)
{
	vector<int> prevCoords = Snake::Advance(step);

	shared_ptr<SnakeSegment> newSegment;
	newSegment = make_shared<SnakeSegment>(SnakeSegment(prevCoords));
	this->_segments.push_back(newSegment);
}

vector<vector<int>> Snake::Points()
{
	vector<vector<int>> points;

	vector<int> head = this->_head->GetCoords();
	points.push_back(head);

	for (shared_ptr<SnakeSegment> segment : this->_segments)
	{
		vector<int> coords = segment->GetCoords();
		points.push_back(coords);
	}

	return points;
}

