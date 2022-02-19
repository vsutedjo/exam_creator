# exam_creator
A tool that automatically creates "exam" sheets from a random set of exercises (from tutorial sheets). This is useful for practising random exercises for a real exam. 

# Setup
- Install all python modules listed in the `main.py` file.
- Install poppler and tesseract. Change the filepaths in `main.py`:
   - Add the poppler filepath to make_pngs at `poppler_path=`
   - Check that the tesseract.exe path is correct in `tesseract_cmd`
- Add your exercise sheet pdfs into a folder `sheets_pdf`.
  - Check the naming pattern. The code assumes `Assignment x.pdf` as pattern. If yours is different, change it in `make_pngs()` under `path=`
# Run
- (optional) run `make_pngs()` with all your sheets to create all possible exercise pngs (this will make future `create_exam()` calls faster).
- call `create_exam()` with the number of problems and the title. Your finished pdf will be saved under exams/. Done:)

# Result:
![readme_image](https://user-images.githubusercontent.com/37225049/154799372-4d0322de-7776-4248-b923-5c25f3a6e482.png)
