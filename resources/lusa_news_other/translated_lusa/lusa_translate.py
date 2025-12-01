
import os
from deep_translator import GoogleTranslator
import random
import time





#Max chars from GoogleTranslate

MAX_CHARS=4900
RESULT_FOLDER="translated_lusa"
TARGET_LANGUAGE="en"

SOURCE_FOLDER_PATH=os.path.join(".")
TARGET_FOLDER=os.path.join(RESULT_FOLDER,TARGET_LANGUAGE)


if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)
    print(f"Folder '{RESULT_FOLDER}' created successfully.")
else:
    print(f"Folder '{RESULT_FOLDER}' already exists.")


if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)
    print(f"Folder '{TARGET_FOLDER}' created successfully.")
else:
    print(f"Folder '{TARGET_FOLDER}' already exists.")



def segmentText(text):
    text_list=[]
    text_words=text.split(" ")
    temp_text=""
    for w in text_words:
        if(len(temp_text)+len(w)>=MAX_CHARS):
            text_list.append(temp_text)
            temp_text=w
        else:
            temp_text=temp_text+ " " +w
    if(len(temp_text)>0):
        text_list.append(temp_text)
    return text_list
def translateTextFromFile(source_file_path,translator):
    with open(source_file_path, 'r') as file:
        text = file.read()
        time.sleep(random.randint(2, 5))


        if (len(text) >= MAX_CHARS):
            text_list = segmentText(text)
            translation = ""
            for text_entry in text_list:
                try:
                    translation = translation + " " + translator.translate(text_entry)
                except Exception as e:
                    translation= translator+ " " + text_entry
        else:
            try:
                translation = translator.translate(text)
            except Exception as e:
                translation= text
    file.close()
    return translation

def translateAnnFromFile(source_file_path,translator):
    res=list()
    translated_res=""
    with open(source_file_path, 'r') as file:
        for line in file:
            # Process each line as desired
            ann_entry = line.split("\t")
            res.append(ann_entry)
    for ann in res:
        if (ann[0].startswith("T")):
            ann_translated=ann
            print(ann)
            text_trans =ann[2].replace("\n","")
            try:
                translation = translator.translate(text_trans)
            except Exception as e:
                print(e)
                translation=text_trans
            ann_translated[2] = translation
            ann_translated="\t".join(ann) + "\n"
            print(ann_translated)

        else:
            ann_translated = "\t".join(ann)
        translated_res=translated_res + ann_translated
    return translated_res










translator = GoogleTranslator(source='pt', target=TARGET_LANGUAGE)

files = os.listdir(SOURCE_FOLDER_PATH)

# Filter out only the .txt files
txt_files = [file for file in files if file.endswith('.txt')]
txt_files.sort()
for t in txt_files:
     translation=translateTextFromFile(os.path.join(SOURCE_FOLDER_PATH,t),translator)
     with open(os.path.join(TARGET_FOLDER,t), 'w') as file:
         file.write(translation)
     print(f"Translation written to '{t}' successfully.")


ann_files = [file for file in files if file.endswith('.ann')]
ann_files.sort()

for a in ann_files:
    ann_translation=translateAnnFromFile(os.path.join(SOURCE_FOLDER_PATH,a),translator)
    with open(os.path.join(TARGET_FOLDER,a), 'w') as file:
        # Write the string to the file
        file.write(ann_translation)



"""

from translated_lusa.modules.mirandes import translate2Mirandes,translateAnn2Mirandes

#TRANSLATION TO MIRANDES


TARGET_LANGUAGE="mirandes"
SOURCE_FOLDER_PATH=os.path.join(".")
TARGET_FOLDER=os.path.join(RESULT_FOLDER,TARGET_LANGUAGE)



if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)
    print(f"Folder '{TARGET_FOLDER}' created successfully.")
else:
    print(f"Folder '{TARGET_FOLDER}' already exists.")





files = os.listdir(SOURCE_FOLDER_PATH)

# Filter out only the .txt files
txt_files = [file for file in files if file.endswith('.txt')]
txt_files.sort()
for t in txt_files:
     translation=translate2Mirandes(os.path.join(SOURCE_FOLDER_PATH,t))
     with open(os.path.join(TARGET_FOLDER,t), 'w') as file:
         file.write(translation)
     print(f"Translation written to '{t}' successfully.")


ann_files = [file for file in files if file.endswith('.ann')][3:]
ann_files.sort()

for a in ann_files:
    ann_translation=translateAnn2Mirandes(os.path.join(SOURCE_FOLDER_PATH,a))
    with open(os.path.join(TARGET_FOLDER,a), 'w') as file:
        # Write the string to the file
        file.write(ann_translation)

"""