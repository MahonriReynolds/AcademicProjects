
#include "Snake.h"
#include "SnakeHead.h"
#include "SnakeSegment.h"

#include "SDL.h"
#undef main

#include <random>
#include <iostream>
#include <vector>

using namespace std;

int main()
{

    // windowing
    int width = 800;
    int height = 600;

    SDL_Init(SDL_INIT_EVERYTHING);
    SDL_Window* window = SDL_CreateWindow("CSE 220C Final", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    // make snake
    Snake snake({ width / 2, height / 2 });
    SDL_Color snakeColor = { 19, 168, 28, 255 };
    vector<vector<int>> snakePoints;
    SDL_Rect snakeBlock;

    // make foods
    SDL_Color foodColor = { 209, 8, 65, 255 };
    vector<int> foods = { (rand() % width / 20) * 20, (rand() % height / 20) * 20 };
    SDL_Rect foodBlock;

    // game loop
    bool run = true;
    SDL_Event event;
    vector<int> direction = { 0, 0 };

    while (run)
    {
        while (SDL_PollEvent(&event))
        {
            if (event.type == SDL_KEYDOWN)
            {
                switch (event.key.keysym.sym)
                {
                case SDLK_LEFT:
                    direction = {-20, 0};
                    break;
                case SDLK_RIGHT:
                    direction = {20, 0};
                    break;
                case SDLK_UP:
                    direction = {0, -20};
                    break;
                case SDLK_DOWN:
                    direction = {0, 20};
                    break;
                case SDLK_ESCAPE:
                    run = false;
                    break;
                }
            }
        }

        // refresh background
        SDL_SetRenderDrawColor(renderer, 65, 65, 65, 255);
        SDL_RenderClear(renderer);

        // update snake
        snake.Advance(direction);
        snakePoints = snake.Points();
        
        // draw snake and check collision
        SDL_SetRenderDrawColor(renderer, snakeColor.r, snakeColor.g, snakeColor.b, snakeColor.a);
        for (int i = 0; i < snakePoints.size(); i++)
        {
            vector<int> point = snakePoints[i];

            snakeBlock = { point[0]-8, point[1]-8, 16, 16 };

            if (i == 0)
            {
                snakeBlock = { point[0] - 10, point[1] - 10, 20, 20 };

                if (point[0] + 10 >= width || point[1] + 10 >= height || point[0] - 20 < 0 || point[1] - 20 < 0)
                {
                    run = false;
                }
                if (point[0] == foods[0] && point[1] == foods[1])
                {
                    snake.Grow(direction);
                    foods = { (rand() % width / 20) * 20, (rand() % height / 20) * 20 };
                }
            }
            else
            {
                if ((snakePoints[0][0] == point[0]) && (snakePoints[0][1] == point[1]))
                {
                    run = false;
                }
            }

            SDL_RenderFillRect(renderer, &snakeBlock);
        }

        // draw foods
        SDL_SetRenderDrawColor(renderer, foodColor.r, foodColor.g, foodColor.b, foodColor.a);
        foodBlock = {foods[0]-5, foods[1]-5, 10, 10};
        SDL_RenderFillRect(renderer, &foodBlock);

        // draw out current render
        SDL_RenderPresent(renderer);
        SDL_Delay(250);
    }

    SDL_DestroyWindow(window);

    return 0;
}
