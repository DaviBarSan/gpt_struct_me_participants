from py_mini_racer import py_mini_racer
import os
# Create a new py_mini_racer context
ctx = py_mini_racer.MiniRacer()

# Load the JavaScript file
with open(os.path.join("translated_lusa","modules","mirandes.js"), "r") as js_file:
    js_code = js_file.read()

# Evaluate the JavaScript code
ctx.eval(js_code)

# Call the JavaScript function
def mirandes(text):
    result = ctx.call("traduz", text)
    return result



def translateAnn2Mirandes(source_file_path):
    res=list()
    translated_res=""
    with open(source_file_path, 'r') as file:
        for line in file:
            # Process each line as desired
            ann_entry = line.split()
            res.append(ann_entry)
    for ann in res:
        if (ann[0].startswith("T")):
            text_trans = " ".join(ann[4:])
            print(text_trans)
            translation = mirandes(text_trans)
            print(translation)
            ann_translated = ann[0:4] + translation.split()
            ann_translated=" ".join(ann_translated)
        else:
            ann_translated = " ".join(ann)
        translated_res=translated_res + ann_translated +"\n"
    file.close()
    return translated_res



def translate2Mirandes(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    f.close()
    return mirandes(text)
