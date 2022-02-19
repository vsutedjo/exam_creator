import math
import os

import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from numpy import random
from pdf2image import convert_from_path


def make_pngs(sheets):
    """
    make_pngs converts a set of exercise sheet pdfs to a folder structured set of pngs, where each exercise
    of each sheet is a different png. The sheet pdfs should be in the "sheet_pdfs" folder.
    This function is called whenever create_exam() needs an exercise png that doesn't exist yet.
    However, it is intended to be used also before create_exam() to create all exercise pngs before creating an exam.
    This way, the exam creation is accelerated because all pngs exist.
    Note: The code assumes the pattern "Assignment xy.pdf" for the sheets. If it is different, change it in the code.
    :param sheets: The exercise sheets that should be converted to pngs. That is, a list of indices of the sheets with
    leading zeros, if necessary.
    :type sheets: list[string]
    :return: None
    :rtype: None
    """
    for sheet in sheets:
        if not os.path.isdir("pngs/"):
            os.mkdir("pngs/")
        if not os.path.isfile("pngs/" + sheet + "/all.png"):
            path = "sheet_pdfs/Assignment " + sheet + ".pdf"
            images = convert_from_path(path, 500,
                                       poppler_path=r"C:/Users/vivia/Downloads/poppler/poppler-22.01.0/Library/bin")
            total_width, total_height = 4134, len(images) * 5300
            result = Image.new('RGB', (total_width, total_height))
            for i in range(len(images)):
                page = images[i]
                result.paste(im=page, box=(0, i * 5300))
            if not os.path.isdir("pngs/" + sheet + "/"):
                os.mkdir("pngs/" + sheet + "/")
            result.save("pngs/" + sheet + "/all.png")
        get_exercise_pngs(sheet)


def get_exercise_pngs(sheet_nr):
    """
    get_exercise_pngs() is a helper function that crops exercise pngs from a stitched sheet png.
    :param sheet_nr: string "index" of the sheet to be cropped
    :type sheet_nr: string
    :return:
    :rtype:
    """
    img = cv2.imread("pngs/" + sheet_nr + "/all.png")
    h, w, _ = img.shape
    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
    boxes = pytesseract.image_to_boxes(img).splitlines()
    rel_boxes = []
    last_char_before_tut = None
    for i in range(len(boxes) - 2):
        box = boxes[i]
        next_box = boxes[i + 1]
        next_next_box = boxes[i + 2]
        box = box.split()

        # Once we have detected a "Tutorial" string, we can stop searching for exercises.
        if last_char_before_tut is None:
            # Check for "Homework" strings that come before any "Tutorial" string.
            if box[0] == "H" and next_box[0] == "o" and next_next_box[0] == "m":
                rel_boxes.append(int(box[2]))
            # Check for a "Tutorial" string and save the last char before it.
            elif next_box[0] == "T" and next_next_box[0] == "u":
                last_char_before_tut = int(box[2])

    # Calculate the crop boxes for the homework exercises.
    # That is, the boxes between two "Homework" titles.
    crop_boxes = []
    for i in range(len(rel_boxes) - 1):
        curr_box = rel_boxes[i]
        next_box = rel_boxes[i + 1]
        crop_boxes.append((curr_box, next_box))

    # If there are tutorial exercises at the end, cut the last exercise before tutorial begins.
    # Else, cut the last exercise at the last detected char minus some offset.
    last_exercise_box = rel_boxes[-1]
    if last_char_before_tut is not None:
        crop_boxes.append((last_exercise_box, last_char_before_tut - 100))
    else:  # Crop it at the last available character.
        crop_boxes.append((last_exercise_box, int(boxes[-1][2]) - 100))

    for i in range(len(crop_boxes)):
        b = crop_boxes[i]
        cropped_img = img[h - b[0] + 20:h - b[1] - 70, 0:w]
        cv2.imwrite("pngs/" + sheet_nr + "/" + str(i + 1) + ".png", cropped_img)


def create_exam(nr_exam_problems, title):
    """
    create_exam automatically creates an exam with given number of problems from existing exercise sheets.
    The exam pdf is saved under exams with the sheet nr (S) and exercise nr (E) in the title, so that
    the user can compare with the respective solutions.
    Note: One can (but doesn't have to) run make_pngs() for all sheets before running create_exam to accelerate the creation time.
    :param nr_exam_problems: The amount of problems that should be included (randomly) in the exam.
    :type nr_exam_problems: int
    :param title: The title of the exam.
    :type title: string
    :return: nothing
    :rtype:
    """
    nr_sheets = 12
    nr_exercises_per_sheet = 4
    images = []
    (total_width, total_height) = 0, 0
    problems = ""
    selected_exercises = []
    for i in range(0, nr_exam_problems):
        rand = random.randint(0, nr_sheets * nr_exercises_per_sheet)

        # Make sure that we don't have the same exercise twice.
        while rand in selected_exercises:
            rand = random.randint(0, nr_sheets * nr_exercises_per_sheet)

        selected_exercises.append(rand)

        sheet = math.floor(rand / nr_exercises_per_sheet) + 1
        if sheet < 10:
            sheet = "0" + str(sheet)
        else:
            sheet = str(sheet)
        exercise = rand % nr_exercises_per_sheet + 1

        # Check if the pngs already exist, otherwise create them.
        png_path = "pngs/" + str(sheet) + "/" + str(exercise) + ".png"
        if not os.path.isfile(png_path):
            make_pngs([sheet])

        # Add the respective png of the exercise to the images.
        image = Image.open(png_path)
        images.append(image)
        total_height += image.size[1]
        total_width = image.size[0]
        problems += "_S" + str(sheet) + "E" + str(exercise)

    # Calculate the heights where to paste the images.
    # That is, the exercise title offset plus image height.
    first_page_height = 700
    text_height = 150
    heights = [first_page_height]
    for i in range(1, len(images)):
        heights.append(heights[i - 1] + images[i - 1].size[1] + text_height)
    result = Image.new('RGB', (total_width, total_height + first_page_height + nr_exam_problems * text_height),
                       (255, 255, 255))

    # Write title
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype("C:/Windows/Fonts/Arialbd.ttf", size=120)
    w, h = draw.textsize(title, font=font)
    draw.text(((total_width - w) / 2, 50), title, (0, 0, 0), font=font)

    # Write working instructions
    left_offset = 200
    top_offset = 300
    nr_problems_title = "Number of problems: "
    working_time_title = "Working time: "

    font = ImageFont.truetype("C:/Windows/Fonts/Arialbd.ttf", size=80)
    w1, h = draw.textsize(nr_problems_title, font=font)
    w2, _ = draw.textsize(working_time_title, font=font)
    draw.text((left_offset, top_offset), nr_problems_title, (0, 0, 0), font=font)
    draw.text((left_offset, top_offset + h + 50), working_time_title, (0, 0, 0), font=font)

    font = ImageFont.truetype("C:/Windows/Fonts/Arial.ttf", size=80)
    draw.text((w1 + left_offset, top_offset), str(nr_exam_problems), (0, 0, 0), font=font)
    draw.text((w2 + left_offset, top_offset + h + 50), str(nr_exam_problems * 25) + " minutes", (0, 0, 0), font=font)

    # Stitch the exercises together with their problem title to one image.
    for i in range(len(images)):
        draw = ImageDraw.Draw(result)
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size=100)
        draw.text((left_offset, heights[i]+15), "Problem " + str(i + 1), (0, 0, 0), font=font)
        img = images[i]
        result.paste(im=img, box=(0, heights[i] + text_height))
    # result.show()
    if not os.path.isdir("exams/"):
        os.mkdir("exams/")
    result.save("exams/exam_" + problems + ".pdf")


if __name__ == '__main__':
    # Uncomment for the first time.
    # make_pngs(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
    create_exam(5, "Efficient Algorithms and Datastructures 1")
