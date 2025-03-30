# All images are    28 x 28
# All images are    RGBA
# All folders have  10773 img
# Total is          107730
# pixel_values[28*y+x]
from PIL import Image
import sys, time


def get_pixels(digit, num):
    # Get image (0 and 1s not alpha)
    im = Image.open(f"./dataset/{digit}/{num}.png", 'r')
    pixel_values = list(im.getdata())
    pixel_values = [0 if p[3] == 0 else 1 for p in pixel_values]

    # Trim extra rows
    pix = []
    for r in range(28):
        if sum(pixel_values[28*r:28*(r+1)]) > 0:
            pix += pixel_values[28*r:28*(r+1)]
    
    # sum(pix[i::28]) > 0
    # del pix[i-1::28]

    # Add buffer
    pix = [0 for i in range(28)] + pix + [0 for i in range(28)]
    return pix


def print_num(pix):
    print('[' + '-'*28 + ']')

    for i, p in enumerate(pix):
        if i % 28 == 0:
            print('[', end='')
        
        pm = " "
        if p == 1:
            pm = "■"
        elif p == 'X':
            pm = 'X'
        elif p == 2:
            pm = '.'

        print(pm, end='')

        if i % 28 == 27:
            print(']')
    
    print('[' + '-'*28 + ']')
    return


def fill(pixels, constraint=None):
    """
    constraint:
        Tuple (dx, dy) indicating the direction that cannot be filled.
        Example: (0, 1) prevents filling to the right.

    Assumes a buffer of at least one space on all sides.
    """
    pixels = pixels.copy()
    start = 14

    # Setup constraint
    height = len(pixels) // 28
    v_mid = height//2

    if constraint is not None:
        mapping = {
            # Down (bottom center)
            (1, 0): (height - 1, 14),
            # Up (top center)
            (-1, 0): (0, 14),
            # Right (right center)
            (0, 1): (v_mid, 27),
            # Left (left center)
            (0, -1): (v_mid, 0)
        }
        r, c = mapping[constraint]
        start = r * 28 + c

    # Start filling
    pixels[start] = 'X'

    while 'X' in pixels:
        active_locations = [i for i, x in enumerate(pixels) if x == "X"]
        
        for p in active_locations:
            row, col = divmod(p, 28)

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                # Don't move in the blocked direction
                if (dx, dy) == constraint:
                    continue
                
                new_row, new_col = row + dx, col + dy
                
                # Ensure within bounds
                if 0 <= new_row < height and 0 <= new_col < 28:
                    new_pos = new_row * 28 + new_col
                    if pixels[new_pos] == 0:
                        pixels[new_pos] = 'X'

            # Mark as visited
            pixels[p] = 2
    return pixels


def score_pix(p):
    return p.count(0) / len(p)


def get_score(pixels):
    """
    Down left half
    Down right half
    Up left half
    Up right half
    Right top half
    Right bottom half
    Left top half
    Left bottom half
    Submerged
    """
    height = len(pixels)//28
    score = []

    # Vertical
    for dir in [(1, 0), (-1, 0)]:
        filled = fill(pixels, dir)
        # Left Half
        score.append(score_pix([filled[r * 28 + c] for r in range(height) for c in range(14)]))
        # Right half
        score.append(score_pix([filled[r * 28 + c] for r in range(height) for c in range(14, 28)]))
    
    # Horizontal
    for dir in [(0, 1), (0, -1)]:
        filled = fill(pixels, dir)
        # Top half
        score.append(score_pix(filled[:len(pixels)//2]))
        # Bottom Half
        score.append(score_pix(filled[len(pixels)//2:]))
    
    # Submerged
    score.append(score_pix(fill(pixels)))

    return score


def score_data():
    """
    All Sides / 2
    (8)
    
    No constraints

    (9)
    """

    # Digit, top_left, bottom_left, 
    scores = []
    print()
    start_time = time.time()
    print('[' + '-'*38 + ']')
    print()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print()
    print('-'*20)
    for digit in range(10):
        for data_point in range(1, 10773):
            pixels = get_pixels(digit, data_point)
            score = get_score(pixels)
            score.append(digit)
            scores.append(score)
            if data_point % (10773//2) == 0:
                print('■',end='')
                sys.stdout.flush()
    print()
    print('-'*20)
    
    with open(f"digit_scores.py", 'w+') as file:
        file.write("digit_scores="+str(scores))

    end_time = time.time()  # Record the end time
    duration = end_time - start_time
    hours, rem = divmod(duration, 3600)
    minutes, seconds = divmod(rem, 60)
    print()
    print(f"Run time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    print()
    print('[' + '-'*38 + ']')
    print()
    return


if __name__ == "__main__":
    # score_data()
    for i in range(10):
        print_num(get_pixels(i, 0))
