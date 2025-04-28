
# Add this snippet to the top of small scripts to generate 
# a variable trace table in the same folder called 'trace.txt'
# Assumes code to be traced is in a function and will be 
# handling variables as locals.


# This is an implimentation of sys.settrace() so import sys.
import sys

# Set up trace function to handle formatting of trace table.
def trace(frame, *_):
    
    # Move the variable names out two tabs which will accomodate up 
    # to 999 lines without messing up the formatting.
    header = '\t\t'
    
    # Start off the next trace line with the line number.
    next_line = f'\n{frame.f_lineno}\t\t'

    # For each local value, turn the name and value into a 
    # string and find the difference in their lengths. 
    # The difference is used to fill the empty distance between 
    # the two so the columns stay aligned in the table.
    for v in frame.f_locals:
        h = str(v)
        n = str(frame.f_locals[v])
        spacer = ' ' * (abs(len(h) - len(n)))
        
        # Check if the header or variable value should receive 
        # the spacer.
        if len(h) > len(n):
            n += spacer
        else:
            h += spacer
        
        # Space each column out by 2 tabs.
        header += f'{h}\t\t'
        next_line += f'{n}\t\t'

    # Use append mode first to gen the file if not exists.
    # Add the next line of value traces.
    with open('trace.txt', 'a') as f:
        f.write(next_line)
    
    # Mode r+ wasn't working so I split it up into r and w modes.
    # file.seek(0, 0) was also giving issues.
    # Read everything out of the trace table file and overwrite 
    # the first line (prev header) with the new header then write 
    # it all back in.
    with open('trace.txt', 'r') as f:
        content = f.readlines()
    content[0] = f'{header}\n'
    with open('trace.txt', 'w') as f:
        f.writelines(content)

    # Return trace for sys to use. 
    return trace

# Use sys to set the trace function as the program trace.
sys.settrace(trace)


# ** main code goes here **
