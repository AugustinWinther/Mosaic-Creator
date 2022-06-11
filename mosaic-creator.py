# Created by Augustin Winther 2022
#
# HEADS UP! This code is awful haha, im so sorry for anyone who sees this :P
#
# But hey, it works... sometimes 
#
# A mosaic is an image built by fragments called "tessera" (plural: "tesserae")
#

# Standard imports
import sys
from sys import argv as cli_args
from os import path, mkdir, remove, rmdir, listdir
from time import time 

# Third party imports
from PIL import Image

# List of allowed image formats
ALLOWED_IMAGE_FORMATS = ["JPEG","PNG","WebP","BMP","DDS","GIF","TIFF"]

def avg_img_color(image_file):
    with Image.open(image_file) as img:
        img_width  = img.size[0]
        img_height = img.size[1]
        pixel = img.load()
        r_tot = 0
        g_tot = 0
        b_tot = 0
        
        # Loop through all pixels in image and add RGB values
        for pixel_column in range(img_width):
            for pixel_row in range(img_height):
                r_tot = r_tot + pixel[pixel_column, pixel_row][0]
                g_tot = g_tot + pixel[pixel_column, pixel_row][1]
                b_tot = b_tot + pixel[pixel_column, pixel_row][2]
        
    # Divides each total channel value by amount of pixels in image
    r_avg = round(r_tot / (img_height * img_width)) 
    g_avg = round(g_tot / (img_height * img_width))
    b_avg = round(b_tot / (img_height * img_width))

    return (r_avg, g_avg, b_avg)

def index_dir(tessera_dir_path):
    # Add trailig \ to direcorty path if its missing
    if tessera_dir_path[-1] != "\\":
        tessera_dir_path = tessera_dir_path + "\\"

    # Create a tessera index directory if it doesn't exist
    index_dir = ".tessera_indexes"
    if not path.exists(index_dir):
        mkdir(index_dir)
    
    # Create a tessera index file using the name of the tessera_dir to be indexed
    index_file = (str(tessera_dir_path).split("\\"))[-2]+".index"
    index_file_path = path.join(index_dir, index_file)
    
    # Create a list of all contents in a dir (recursive), and add full path to all
    def dir_content_to_list(dir):
        content_list = []
        for content in listdir(dir):
            content_path = path.join(dir, content)
            if path.isdir(content_path):
                content_list = content_list + dir_content_to_list(content_path)
            else: 
                content_list.append(content_path)
        return content_list

    # Get all contents from passed tessera dir
    tessera_dir_content = dir_content_to_list(tessera_dir_path)

    # Create a list to hold all tesserae to be indexed
    non_indexed_tesserae = []

    # If a tessera index_file for this folder already exists, check if it is up to date
    if path.exists(index_file_path):
        # Add all tesserae in the index file to a list
        indexed_tesserae = []
        with open(index_file_path) as file:
            for line in file: 
                text = line.split(" | ")
                tessera = text[0]
                indexed_tesserae.append(tessera)
        # Add tesseras not indexed in index file to non_indexed_tesserae
        for tessera in tessera_dir_content:
            if tessera not in indexed_tesserae:
                non_indexed_tesserae.append(tessera)
        # Retrivev the lines in the index file containing non exisiting tesserae
        line_nums_to_delete = []
        for tessera in indexed_tesserae:
            if tessera not in tessera_dir_content:
                line_nums_to_delete.append(indexed_tesserae.index(tessera)+1)
        # Delete all lines containing non exisiting tesserae
        if len(line_nums_to_delete) > 0:
            with open(index_file_path, 'r') as file_info:
                lines = file_info.readlines()
                line_num = 1
                with open(index_file_path, 'w') as file:
                    for line in lines:
                        if line_num not in line_nums_to_delete:
                            file.write(line)
                        line_num += 1

    # If there is no index_file, then all contents in tessera dir will be added to non_indexed_tesserae
    else: 
        non_indexed_tesserae = tessera_dir_content
        open(index_file_path, 'a').close() #Create index file

    # Index all tesserae in non_indexed_tesserae
    with open(index_file_path, "a") as tessera_file:
        for tessera in non_indexed_tesserae:
            try:
                tessera_color = avg_img_color(tessera)
            except:
                continue # Skip file if it couldnt be used (possbily not an image file)
            
            avg_red = str(tessera_color[0])
            avg_green = str(tessera_color[1])
            avg_blue = str(tessera_color[2])
            tessera_file.write(f"{tessera} | {avg_red} | {avg_green} | {avg_blue}\n")

    return index_file_path

def check_input(input_image=None, mosaic_width=None, mosaic_height=None, tessera_res=None, tessera_dir=None):
    # Check input image for errors
    if input_image != None:
        if path.exists(input_image):
            try: 
                with Image.open(input_image) as image:
                    if image.format not in ALLOWED_IMAGE_FORMATS:
                        print(" Input image not supported!\n"
                              " Please use PNG, JPEG, WebP, GIF, BMP, DDS, or TIFF\n")
                        clean_and_quit()
            except:
                print(f" {input_image} is not an image!\n"
                       " Please use PNG, JPEG, WebP, GIF, BMP, DDS, or TIFF\n")
                clean_and_quit() 
        else:
            print(f" input_image: {input_image} does not exist!\n")
            clean_and_quit()

    # Check mosaic_width and mosaic_height for errors
    if mosaic_width != None and mosaic_height != None:
        if (mosaic_width != 0 and mosaic_height != 0):
            if mosaic_width < 2 or mosaic_width > 512:
                print(f" mosaic_width = {mosaic_width} is invalid!\n"
                       " mosaic_width can't be less than 2, or greater than 512!\n")
                clean_and_quit()
            elif mosaic_height < 2 or mosaic_height > 512:
                print(f" mosaic_height = {mosaic_height} is invalid!\n"
                       " mosaic_height can't be less than 2, or greater than 512!\n")
                clean_and_quit()

    # Check tessera_res for errors
    if tessera_res != None:
        if tessera_res < 1 or tessera_res > 64:
            print(f" tessera_res = {tessera_res} is invalid!\n"
                   " tessera_res can't be less than 1, or greater than 64!\n")
            clean_and_quit()

    # Check tessera_dir folder for errors
    if tessera_dir != None:
        if path.exists(tessera_dir):
            if not (path.isdir(tessera_dir)):
                print(f"   tessera_dir: {tessera_dir} is not a folder/directory!\n")
                clean_and_quit()
        else:
            print(f" tessera_dir: {tessera_dir} does not exist!\n")
            clean_and_quit()

def index_to_list(tessera_index):
    list = []

    with open(tessera_index) as file:
        for line in file: 
            text = line.split(" | ")
            tessera = text[0]
            color = (int(text[1]),int(text[2]),int(text[3]))  # (R,G,B)
            list.append([tessera, color])
    return list

def resize_image(input_image, width, height):

    with Image.open(input_image) as image:
        if (width == 0 and height != 0):
            width = round(image.size[0] * (height / image.size[1]))
        elif (width != 0 and height == 0):
            height = round(image.size[1] * (width / image.size[0]))
        elif (width == 0 and height == 0):
            width = image.size[0]
            height = image.size[1]   
        resized_image = image.resize((width, height))

    return resized_image

def resize_tessera(tessera_path, tessera_res):

    # Create path to a cached version of the resized tessera
    tessera_file = (tessera_path.split("\\"))[-1]
    tessera_cache_path = path.join(CACHE_DIR, tessera_file)

    # If a cached version of the resized tessera already exisit, use that one. If not, resize this and cache it
    if path.exists(tessera_cache_path):
        tessera_resized = tessera_cache_path
    else:
        tessera_resized = resize_image(tessera_path, 0, tessera_res)
        tessera_resized.save(tessera_cache_path)
        tessera_resized = tessera_cache_path

    return tessera_resized

def pixel_to_tessera(pixel, tessera_list):
    # Just some starting values... 
    # These will always change in the for loop
    min_rgb_diff = 1000
    tessera = None

    for index in tessera_list: 
        color_rgb = index[1]
        rgb_diff = (abs(pixel[0] - color_rgb[0])
                  + abs(pixel[1] - color_rgb[1])
                  + abs(pixel[2] - color_rgb[2]))
        if rgb_diff < min_rgb_diff:
            min_rgb_diff = rgb_diff
            tessera = index[0]
    return tessera

def check_mosaic_name(mosaic_name):
    # Genereate output mosaic filename
    if "\\" in mosaic_name:
        mosaic_name = (mosaic_name.split("\\"))[-1]
    
    # Set extension
    if mosaic_name.split(".")[-1] == "gif":
        extension = ".gif"
    else:
        extension = ".png"

    # Create default name
    mosaic_name = (mosaic_name.split("."))[0] + "-mosaic" + extension

    # Make sure a file with thaht name does not exist, and give user options if it does
    if path.exists(mosaic_name):
        answer = ""
        while answer != "r" and answer != "n" and answer != "q":
            answer = input(f"\n A mosaic named {mosaic_name} already exists!\n"
                              "   Do you want to replace this mosaic?     [r]\n"
                              "   or create a new mosaic with a new name? [n]\n"
                              "   or quit the mosiaic-creator?            [q]\n\n"
                              " type youre choice followed by enter [r/n/q]: ")
            if answer == "n":
                name = input("\n Please type your desired mosaic name: ")
                mosaic_name = name + extension
                if path.exists(mosaic_name):
                    answer = ""  # Go back to start of answer loop if this filename is taken
                else:
                    return mosaic_name # Return new mosaic name
            elif answer == "q":
                print(f"\n Quitting...")
                clean_and_quit()
            elif answer == "r":
                return mosaic_name # Return same mosaic name as passed
    else:
        return mosaic_name # Return same mosaic name as passed
    
def image_to_mosaic(input_image, tessera_list, tessera_res):
    # Mosaic image to paste the tesseras to   
    output_mosaic = Image.new('RGB', ((input_image.size[0]*tessera_res), 
                                      (input_image.size[1]*tessera_res)))

    # Set "pixel_data" to be equal to the pixel information from input_image
    pixel_data = input_image.load()

    # Define default values to be used in the converting algorithm
    pixel_x = 0
    pixel_y = 0
    max_x = input_image.size[0] - 1
    max_y = input_image.size[1] - 1
    pixel_count = (max_x + 1) * (max_y + 1)
    pixel_conv_time = 0
    time_since_last_conv = time()
    eta_string = ""
    last_eta_print = time()
    last_percent = -1

    #Time exec.
    start_time = time()

    # START OF CONVERTING
    while pixel_x <= max_x:
        
        # Calculate time used to convert 100 pixels
        pixel_conv = (pixel_x) * (max_y) + pixel_y
        if (pixel_conv % 100 == 0):
            pixel_conv_time = time() - time_since_last_conv
            time_since_last_conv = time() 
    
        # Create and print progress bar and ETA
        if (time() - last_eta_print >= 1):
            eta = pixel_conv_time*((pixel_count - pixel_conv)/100)
            eta_sec = eta % 60
            eta_min = eta / 60
            eta_string = " ETA: %dm %ds "  % (eta_min, eta_sec)
            last_eta_print = time()
        percent = round((pixel_x / max_x) * 100)
        if (percent > last_percent):
            last_percent = percent
            percent_left = 100 - percent
            progress_bar = ((round(percent / 2) * '█' ) 
                        + (round(percent_left / 2) * '-'))
            print(f" Progress: {progress_bar} {percent}% {eta_string}", end="\r")

        # Current pixel
        pixel = pixel_data[pixel_x, pixel_y]

        # Convert the pixel to a tessera and paste it to the output_mosaic
        tessera = pixel_to_tessera(pixel, tessera_list)
        tessera = resize_tessera(tessera, tessera_res)
        tessera_pos = ((pixel_x*tessera_res),(pixel_y*tessera_res))
        with Image.open(tessera) as tessera_img:
            output_mosaic.paste(tessera_img, tessera_pos)
        
        # Increase pixel count at and of while loop
        if (pixel_y < max_y):
            pixel_y += 1
        else:
            pixel_y = 0
            pixel_x += 1
        
    # END OF CONVERTING

    # Calculate and print execution time
    time_passed = (time() - start_time)
    sec_passed = time_passed % 60
    min_passed = time_passed / 60
    print(f"\n Finished in: {min_passed:.0f}min {sec_passed:.3f}sec\n")

    return output_mosaic

def clean_and_quit():
    # Delete all temp folders if they exist
    if path.exists(CACHE_DIR):
        for file in listdir(CACHE_DIR):
            file_path = path.join(CACHE_DIR, file)
            remove(file_path)
        rmdir(CACHE_DIR) 
    sys.exit()

if __name__ == "__main__":
    # Just for nice looks in cli
    print("")

    # Create cache folder if it does not exist
    CACHE_DIR = ".tessera_cache"
    if not path.exists(CACHE_DIR):
        mkdir(CACHE_DIR)

    # Check that enough arguments are passed
    if len(cli_args) < 6:
        print(" Too few options!\n"
              " Script usage: python mosaic-creator.py " 
              " <input_image> <mosaic_width> <mosaic_height> <tessera_res> <tessera_folder> \n")
        clean_and_quit()

    # Try to assign correct data type to input values
    try:
        input_image = str(cli_args[1])
    except:
        print(f" input_image: {cli_args[1]} is not a string!\n")
        clean_and_quit()

    try:
        mosaic_width = int(cli_args[2])
    except:
        print(f" mosaic_width: {cli_args[2]} is not a integer!\n")
        clean_and_quit()
    
    try:
        mosaic_height = int(cli_args[3])
    except:
        print(f" mosaic_height: {cli_args[3]} is not a integer!\n")
        clean_and_quit()
            
    try:
        tessera_res = int(cli_args[4])
    except:
        print(f" tessera_res: {cli_args[4]} is not a integer!\n")
        clean_and_quit()

    # Check input values for errors
    check_input(input_image=input_image, 
                mosaic_width=mosaic_width, 
                mosaic_height=mosaic_height, 
                tessera_res=tessera_res)

    # Add all passed tessera folders and check them for faults
    print(" Indexing tessera folder(s)... Please Wait")
    tessera_list = []
    for tessera_folder in cli_args[5:]:
        # Remove trailing '"' from folder path if exists
        if tessera_folder[-1] == '"':
            tessera_folder = tessera_folder[0:-1]
        # Check tessera folder and add all the contents to a list
        check_input(tessera_dir=tessera_folder)
        print(f"   Indexing {tessera_folder} ...")
        tessera_file = index_dir(tessera_folder)
        tessera_list = tessera_list + (index_to_list(tessera_file))
    print(" Done!")

    # Get name and format from image
    with Image.open(input_image) as image:        
        image_name = image.filename
        image_format = image.format
    
    # If input_image is a GIF
    if image_format == "GIF":
        # Create output name and check if it exists
        mosaic_name = f"{image_name}_mosaic.gif"
        mosaic_name = check_mosaic_name(mosaic_name)
        
        # Loop through all frames in GIF
        with Image.open(input_image) as image: 
            frame_list = []
            frame_amount = image.n_frames
            for frame_count in range(frame_amount):
                # Get frame and create temp save path
                frame = image.seek(frame_count)
                frame_path = path.join(CACHE_DIR, f"frame_raw_{frame_count}.png")
                
                # Save frame, convert it to RGB and save it again dont know how else to do it lol
                image.save(frame_path, append_images=[frame])
                with Image.open(frame_path) as frame:
                    frame = frame.convert("RGB")
                    frame.save(frame_path)
                
                # Convert frame to mosaic
                print(f"\n Converting frame {frame_count+1} of {frame_amount}")
                resized_frame = resize_image(frame_path, mosaic_width, mosaic_height)
                converted_frame = image_to_mosaic(resized_frame, tessera_list, tessera_res)
                frame_list.append(converted_frame)
                remove(frame_path) # Delete raw temp frame
                frame_count += 1

            # Compile mosaic gif
            print(f" Saving to: {mosaic_name} ... Please Wait!")
            frame_list[0].save(mosaic_name, save_all=True, append_images=frame_list[1:], loop=0)
            print(" Done!\n")
    
    # If input_image is static image
    else: 
        # Create output name and check if it exists
        mosaic_name = f"{image_name}_mosaic.png"
        mosaic_name = check_mosaic_name(mosaic_name) 

        resized_image = resize_image(input_image, mosaic_width, mosaic_height)
        
        # Inform user about the size of the image, before proceding
        output_width = resized_image.size[0] * tessera_res
        output_height = resized_image.size[1] * tessera_res
        megapixels = (output_width*output_height)/1000000
        answer = None
        print(f"\n Your mosaic will be {output_width}x{output_height} pixels (~ {megapixels:.1f} MP)\n")
        while answer == None:
            answer = input(" Do you want to continue? [y/n] ")
            if answer == "y":
                continue
            elif answer == "n":
                clean_and_quit()
            else:
                answer = None

        # Start converting the image to a mosaic
        print(f"\n Converting: {image_name}")
        converted_image = image_to_mosaic(resized_image, tessera_list, tessera_res)

        print(f" Saving to: {mosaic_name} ... Please Wait!")
        converted_image.save(mosaic_name)
        print(" Done!\n")


    # Deletes tessera cache dir when done
    for file in listdir(CACHE_DIR):
        file_path = path.join(CACHE_DIR, file)
        remove(file_path)
    rmdir(CACHE_DIR) 