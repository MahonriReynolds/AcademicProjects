
use crossterm::{
    event::{self, KeyCode, KeyEvent},
    terminal,
    ExecutableCommand,
    cursor
};
use std::{
    io::{self, Write}, 
    time::{Duration, Instant}, 
    error::Error,
    thread::sleep
};
use rand::Rng; 



struct Grid {
    rows: usize,
    cols: usize,
    data: Vec<Vec<char>>
}

impl Grid {
    fn new(rows: usize, cols: usize) -> Self {
        let data = vec![vec![' '; cols]; rows];
        Grid { rows, cols, data }
    }

    fn display(&self, header: &str, boids: &[Boid], pois: &[POI], selected_poi_index: &usize) {

        print!("\x1b[H"); // Move the cursor to the top of the terminal

        // Check if there are POIs
        if pois.is_empty() {
            println!("\r\x1B[2K{} | POI: 0/0 (+ Insert, - Delete)", header);
        } else {
            // Get POI details for the header
            let total_pois = pois.len();
            
            // Ensure the selected POI index is valid
            if *selected_poi_index < total_pois {
                let selected_poi = &pois[*selected_poi_index];
                let poi_status = if selected_poi.toggled { "Attract" } else { "Repel" };
                println!("\r\x1B[2K{} - POI: (0..9 Select) {}/{} (+ Insert, - Delete) {} (Tab)", header, *selected_poi_index + 1, total_pois, poi_status);
            }
        }
    
        let mut grid_data = self.data.clone();

        // Place Boids on the grid
        for boid in boids {
            let x = boid.position.0.round() as usize;
            let y = boid.position.1.round() as usize;
    
            if x < self.cols && y < self.rows {
                grid_data[y][x] = get_direction_symbol(boid.velocity); // Mark Boid position
            }
        }
    
    
        // Create a lookup map to associate grid positions with POIs
        let poi_map: Vec<(usize, usize, &POI)> = pois.iter().enumerate()
            .map(|(_, poi)| {
                let x = poi.position.0.round() as usize;
                let y = poi.position.1.round() as usize;
                (x, y, poi)
            })
            .collect();
    
        // Place POIs on the grid with the correct symbols
        for (i, poi) in pois.iter().enumerate() {
            let x = poi.position.0.round() as usize;
            let y = poi.position.1.round() as usize;
    
            if x < self.cols && y < self.rows {
                // If this POI is selected, mark it as 'o', else '*' for other POIs
                let symbol = if i == *selected_poi_index { 'o' } else { '*' };
                grid_data[y][x] = symbol;
            }
        }
    
        // Print the grid with POIs and Boids, applying color for each grid cell
        for row in 0..self.rows {
            let row_str: String = (0..self.cols).map(|col| {
                let symbol = grid_data[row][col];
                if let Some((_, _, poi)) = poi_map.iter().find(|(x, y, _)| *x == col && *y == row) {
                    // Color based on POI's toggled state
                    let color = if poi.toggled {
                        32 // Green for toggled POIs
                    } else {
                        31 // Red for untoggled POIs
                    };
    
                    // Format color output for the grid cell
                    format!("\x1b[{}m{}\x1b[0m", color, symbol)
                } else if symbol == '@' {
                    // Handle Boid case with color for Boid symbol '@'
                    "\x1b[34m@\x1b[0m".to_string() // Blue color for Boids
                } else {
                    symbol.to_string() // For empty cells, print normally
                }
            }).collect::<String>();
    
            println!("\r{}", row_str); // Print each row with colors
        }
    
        std::io::stdout().flush().unwrap(); // Ensure the output is immediately displayed
    }
    
    
}

struct POI {
    position: (f32, f32),
    toggled: bool,
}

impl POI {
    fn new(x: f32, y: f32) -> POI {
        POI {
            position: (x, y),
            toggled: true,
        }
    }

    fn toggle(&mut self) {
        self.toggled = !self.toggled;
    }

    fn step(&mut self, direction: (f32, f32)) {
        self.position.0 += direction.0;
        self.position.1 += direction.1;
    }
}

#[derive(Clone, PartialEq)]
struct Boid {
    position: (f32, f32),
    velocity: (f32, f32)
}

impl Boid {
    fn new(x: f32, y: f32, vx: f32, vy: f32) -> Boid {
        Boid {
            position: (x, y),
            velocity: (vx, vy)
        }
    }

    fn update(&mut self, space_width: f32, space_height: f32, boids: &[Boid], pois: &[POI]) {
        let separation_force = self.separation(boids);
        let alignment_force = self.alignment(boids);
        let cohesion_force = self.cohesion(boids);
        let seek_force = self.seek(pois);
    
        self.velocity.0 += separation_force.0 * 1.5 + alignment_force.0 + cohesion_force.0 * 0.75 + seek_force.0 * 0.75;
        self.velocity.1 += separation_force.1 * 1.5 + alignment_force.1 + cohesion_force.1 * 0.75 + seek_force.1 * 0.75;

        // Normalize the velocity if it's too fast
        let speed = (self.velocity.0.powi(2) + self.velocity.1.powi(2)).sqrt();
        if speed > 1.0 {
            let scale = 1.0 / speed;
            self.velocity.0 *= scale;
            self.velocity.1 *= scale;
        }
    
        // Move the Boid by its velocity
        self.position.0 += self.velocity.0;
        self.position.1 += self.velocity.1;
    
        // Bounce away from the left/right walls
        if self.position.0 <= 0.0 {
            self.position.0 = 0.0; // Keep it at the left boundary
            self.velocity.0 *= -1.0; // Reverse horizontal velocity
        } else if self.position.0 >= space_width {
            self.position.0 = space_width; // Keep it at the right boundary
            self.velocity.0 *= -1.0; // Reverse horizontal velocity
        }

        // Bounce away from the top/bottom walls
        if self.position.1 <= 0.0 {
            self.position.1 = 0.0; // Keep it at the top boundary
            self.velocity.1 *= -1.0; // Reverse vertical velocity
        } else if self.position.1 >= space_height {
            self.position.1 = space_height; // Keep it at the bottom boundary
            self.velocity.1 *= -1.0; // Reverse vertical velocity
        }
    }

    fn seek(&self, pois: &[POI]) -> (f32, f32) {
        let mut seek_force = (0.0, 0.0);
        
        for poi in pois {
            let diff_x = poi.position.0 - self.position.0;
            let diff_y = poi.position.1 - self.position.1;
            let distance = (diff_x.powi(2) + diff_y.powi(2)).sqrt();
    
            // Only consider POIs within the max_distance
            if distance < 20.0 {
                let norm_x = if distance != 0.0 { diff_x / distance } else { 0.0 };
                let norm_y = if distance != 0.0 { diff_y / distance } else { 0.0 };
        
                if poi.toggled {
                    seek_force.0 += norm_x;
                    seek_force.1 += norm_y;
                } else {
                    seek_force.0 -= norm_x;
                    seek_force.1 -= norm_y;
                }
            }
        }
    
        seek_force
    }
    
    fn separation(&self, boids: &[Boid]) -> (f32, f32) {
        let mut steer = (0.0, 0.0);
        let mut count = 0;
    
        for other in boids {
            if other != self {
                let dist = ((self.position.0 - other.position.0).powi(2)
                            + (self.position.1 - other.position.1).powi(2))
                    .sqrt();
                
                if dist < 3.0 {
                    let diff = (
                        self.position.0 - other.position.0,
                        self.position.1 - other.position.1,
                    );
                    let magnitude = (dist.max(1.0)).powi(2);
                    steer.0 += diff.0 / magnitude;
                    steer.1 += diff.1 / magnitude;
                    count += 1;
                }
            }
        }
    
        if count > 0 {
            steer.0 /= count as f32;
            steer.1 /= count as f32;
        }
    
        // Normalize the steering force and return
        let length = (steer.0.powi(2) + steer.1.powi(2)).sqrt();
        if length > 0.0 {
            steer.0 /= length;
            steer.1 /= length;
        }
    
        steer
    }

    fn alignment(&self, boids: &[Boid]) -> (f32, f32) {
        let mut sum_velocity = (0.0, 0.0);
        let mut count = 0;
    
        for other in boids {
            if other != self {
                let dist = ((self.position.0 - other.position.0).powi(2)
                            + (self.position.1 - other.position.1).powi(2))
                    .sqrt();
    
                // Consider only nearby Boids for alignment (within a certain radius)
                if dist < 4.0 {
                    sum_velocity.0 += other.velocity.0;
                    sum_velocity.1 += other.velocity.1;
                    count += 1;
                }
            }
        }
    
        if count > 0 {
            sum_velocity.0 /= count as f32;
            sum_velocity.1 /= count as f32;
        }
    
        // Normalize the velocity to keep the boid's movement consistent
        let length = (sum_velocity.0.powi(2) + sum_velocity.1.powi(2)).sqrt();
        if length > 0.0 {
            sum_velocity.0 /= length;
            sum_velocity.1 /= length;
        }
    
        sum_velocity
    }

    fn cohesion(&self, boids: &[Boid]) -> (f32, f32) {
        let mut center_of_mass = (0.0, 0.0);
        let mut count = 0;
    
        // Sum up the positions of nearby boids
        for other in boids {
            if other != self {
                let dist = ((self.position.0 - other.position.0).powi(2)
                            + (self.position.1 - other.position.1).powi(2))
                    .sqrt();
    
                // Consider only nearby Boids for cohesion (within a certain radius)
                if dist < 5.0 {
                    center_of_mass.0 += other.position.0;
                    center_of_mass.1 += other.position.1;
                    count += 1;
                }
            }
        }
    
        // If there are nearby boids, calculate the center of mass and steer towards it
        if count > 0 {
            center_of_mass.0 /= count as f32;
            center_of_mass.1 /= count as f32;
            
            // Calculate the steering force towards the center of mass
            let mut diff = (center_of_mass.0 - self.position.0, center_of_mass.1 - self.position.1);
            
            // Normalize the steering force
            let length = (diff.0.powi(2) + diff.1.powi(2)).sqrt();
            if length > 0.0 {
                diff.0 /= length;
                diff.1 /= length;
            }
    
            return diff;
        }
    
        // If no other boids are nearby, return a neutral force
        (0.0, 0.0)
    }
    
}

fn get_direction_symbol(velocity: (f32, f32)) -> char {
    let abs_x = velocity.0.abs();
    let abs_y = velocity.1.abs();

    if abs_x > abs_y {
        // Horizontal movement (left or right)
        if velocity.0 > 0.0 {
            '⇒'  // Right
        } else {
            '⇐'  // Left
        }
    } else if abs_y > abs_x {
        // Vertical movement (up or down)
        if velocity.1 > 0.0 {
            '⇓'  // Down
        } else {
            '⇑'  // Up
        }
    } else {
        // Diagonal movement (approx. 45 degrees)
        if velocity.0 > 0.0 && velocity.1 < 0.0 {
            '⇗'  // Up-Right
        } else if velocity.0 < 0.0 && velocity.1 < 0.0 {
            '⇖'  // Up-Left
        } else if velocity.0 > 0.0 && velocity.1 > 0.0 {
            '⇘'  // Down-Right
        } else if velocity.0 < 0.0 && velocity.1 > 0.0 {
            '⇙'  // Down-Left
        } else {
            // If there is no movement, we can return a default symbol
            '•'  // Some placeholder for a boid with no movement
        }
    }
}


fn main() -> Result<(), Box<dyn Error>> {
    let mut stdout = io::stdout();
    terminal::enable_raw_mode().unwrap();
    stdout.execute(terminal::Clear(terminal::ClearType::All))?;
    stdout.execute(cursor::Hide)?;

    let (mut cols, mut rows) = terminal::size().unwrap();
    rows = (rows as f32 * 0.9).floor() as u16;
    cols = (cols as f32 * 0.9).floor() as u16;
    let grid = Grid::new(rows.into(), cols.into());

    let mut pois: Vec<POI> = Vec::new();
    let mut boids: Vec<Boid> = Vec::new();

    let start_time = Instant::now();
    let target_duration = Duration::from_millis(33);
    let mut selected_poi_index = 0;

    loop {
        let loop_start = Instant::now();

        if event::poll(Duration::from_millis(33))? {
            if let event::Event::Key(KeyEvent { code, .. }) = event::read()? {
                match code {
                    
                    KeyCode::Left => {
                        if pois.len() > selected_poi_index {
                            let poi = &mut pois[selected_poi_index];
                            let new_x = poi.position.0 - 1.0;
                            // Ensure the POI does not go beyond the left edge (x >= 0)
                            if new_x >= 0.0 {
                                poi.step((-1.0, 0.0));
                            }
                        }
                    },
                    KeyCode::Right => {
                        if pois.len() > selected_poi_index {
                            let poi = &mut pois[selected_poi_index];
                            let new_x = poi.position.0 + 1.0;
                            // Ensure the POI does not go beyond the right edge (x < cols)
                            if new_x < cols as f32 {
                                poi.step((1.0, 0.0));
                            }
                        }
                    },
                    KeyCode::Up => {
                        if pois.len() > selected_poi_index {
                            let poi = &mut pois[selected_poi_index];
                            let new_y = poi.position.1 - 1.0;
                            // Ensure the POI does not go above the top edge (y >= 0)
                            if new_y >= 0.0 {
                                poi.step((0.0, -1.0));
                            }
                        }
                    },
                    KeyCode::Down => {
                        if pois.len() > selected_poi_index {
                            let poi = &mut pois[selected_poi_index];
                            let new_y = poi.position.1 + 1.0;
                            // Ensure the POI does not go below the bottom edge (y < rows)
                            if new_y < rows as f32 {
                                poi.step((0.0, 1.0));
                            }
                        }
                    },
                    
                    KeyCode::Tab => {
                        if pois.len() > selected_poi_index {
                            pois[selected_poi_index].toggle();
                        }
                    },

                    KeyCode::Insert => {
                        if pois.len() < 10 {
                            let center_x = (cols as f32 / 2.0).floor();
                            let center_y = (rows as f32 / 2.0).floor();
                            let new_poi = POI::new(center_x, center_y);
                            
                            pois.push(new_poi);
                            selected_poi_index = pois.len() - 1;
                        }
                    }
                    KeyCode::Delete => {
                        if !pois.is_empty() {
                            pois.remove(selected_poi_index);
                            if selected_poi_index >= pois.len() {
                                selected_poi_index = pois.len().saturating_sub(1);
                            }
                        }
                    }
                    KeyCode::Char('1') => {
                        if pois.len() > 0 {
                            selected_poi_index = 0;
                        }
                    },
                    KeyCode::Char('2') => {
                        if pois.len() > 1 {
                            selected_poi_index = 1;
                        }
                    },
                    KeyCode::Char('3') => {
                        if pois.len() > 2 {
                            selected_poi_index = 2;
                        }
                    },
                    KeyCode::Char('4') => {
                        if pois.len() > 3 {
                            selected_poi_index = 3;
                        }
                    },
                    KeyCode::Char('5') => {
                        if pois.len() > 4 {
                            selected_poi_index = 4;
                        }
                    },
                    KeyCode::Char('6') => {
                        if pois.len() > 5 {
                            selected_poi_index = 5;
                        }
                    },
                    KeyCode::Char('7') => {
                        if pois.len() > 6 {
                            selected_poi_index = 6;
                        }
                    },
                    KeyCode::Char('8') => {
                        if pois.len() > 7 {
                            selected_poi_index = 7;
                        }
                    },
                    KeyCode::Char('9') => {
                        if pois.len() > 8 {
                            selected_poi_index = 8;
                        }
                    },
                    KeyCode::Char('0') => {
                        if pois.len() > 9 {
                            selected_poi_index = 9;
                        }
                    },

                    KeyCode::Enter => {
                        boids.push(Boid::new(
                            rand::thread_rng().gen_range(0.0..cols as f32),
                            rand::thread_rng().gen_range(0.0..rows as f32),
                            rand::thread_rng().gen_range(-10.0..10.0 as f32),
                            rand::thread_rng().gen_range(-10.0..10.0 as f32),
                        ));
                    }
                    KeyCode::Backspace => {
                        if !boids.is_empty() {
                            boids.pop();
                        }
                    }

                    KeyCode::Esc => {
                        println!("\r");
                        terminal::disable_raw_mode().unwrap();
                        stdout.execute(cursor::Show)?;
                        break Ok(());
                    }
                    _ => {}
                }
            }
        }

        let elapsed = start_time.elapsed();
        let secs = elapsed.as_secs_f32();

        let time_str = format!("Time: {:.1}s (Esc)", secs);
        let boid_count_str = format!("Boids: {} (+ Enter, - Backspace)", boids.len());
        let header = format!("{} | {}", time_str, boid_count_str);

        let boids_copy = boids.clone();
        for boid in &mut boids {
            boid.update(cols as f32, rows as f32, &boids_copy, &pois)
        }

        grid.display(&header, &boids, &pois, &selected_poi_index);

        let iteration_duration = loop_start.elapsed();

        // If the iteration was too fast, sleep for the remaining time
        if iteration_duration < target_duration {
            sleep(target_duration - iteration_duration);
        }
    }
}


