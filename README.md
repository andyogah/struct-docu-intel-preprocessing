### summary
this repo works mostly for scanned documents, particular PDFs of poor quality (this will be extended to other data formats in future). this also works for text PDFs too (refer to "usage" section below). there is no goal here, just personal hacking stuff i do from time to time, so opening it up for anyone else to hack away.

</br>

### hints
the following questions will hopefully point you in the right path:
1. what type of document are you working on: text or scanned (pdf in this case)?
2. how do you know it is one vs the other? 
    - can you do a "ctrl f" on it? 
    - can you select, copy and paste on the text? 
    - how was it generated?
3. how good is the quality? 

answers to some or all of these questions will determine preprocessing steps and sequence and subsequently the options you turn off or on below. 

why? 

for example:
1. if a document is all text pdf and of good quality, you don't need to turn on the "preprocessing options" because they are primarily for images/scanned documents. you also don't need to turn on "convert_pdf" because document is already good
2. if a document is text pdf, but of bad quality, converting it to image may help because then you can use those preprocessing options to try to improve extraction accuracy. also, document intelligence is optimized for images because it is built on ai vision (low-level). i will introduce ai vision as an option later, so we can mix and match low and high-level extraction abilites. 
3. if a document is already an image or scanned, it doesn't make sense using "convert_pdf" to image because that is double whammy, making the quality worse. But then, you may be able to play around with the models and all other options.

hope you see where i am going here: knowing the type or properties of the document (s) can help a lot. 

also, knowing the model type is important. there are tons of prebuilt models in azure document intelligence, and each serve a particular purpose. for example, prebuilt-read models won't work for key-value extraction because they are the basic level words, paragraphs, locations extraction. 

if you or we can answer these questions, then we are ready to move on to "set up" and "usage" of this resource.

</br>

### usage

you just need to point to your file location (either url or local path), point to the endpoint of func app, either local or remote, set the boolean options for your payload and send it as a request in code or power app/automate http action. no api-keys required

```

with open(file_path, "rb") as f:
        file_bytes = f.read()

    # Determine file type
    file_extension = os.path.splitext(file_path)[1].lower()
    is_pdf = file_extension == '.pdf'
    
    # Encode as base64
    file_base64 = base64.b64encode(file_bytes).decode()

    # Set options
    payload = {
        "file_data": file_base64,
        "file_type": file_extension[1:],  # Remove the dot
        "options": {
            "convert_pdf": False,
            "preprocess_images": True,
            "analyze_layout": True,
            "analyze_content": True,
            "use_vision_api": use_vision_api
        },
        "model": "prebuilt-document" if not is_pdf else "prebuilt-layout",
        "preprocessing_options": {
            "apply_grayscale": True,
            "apply_blur": False,
            "apply_threshold": False,
            "apply_edge_detection": False
        }
    }

    # Call the API
    # For local testing, use http://localhost:7071
    # For deployed function app, use https://your-function-app.azurewebsites.net
    response = requests.post(
        "http://localhost:7071/api/process_document",
        json=payload
    )

```

- you want to flip the switch on preprocessing options for ocr if you are processing scanned images or pdf. 
- if however, you are working with text PDFs, the "convert_pdf" option in the payload just needs to set to "false." this implies that each of those function "options" can be set and called independently and/or set or called in combination with other function "options"
- the model option allows you try different document intelligence models to see which one works best for your case:
  - prebuilt-document
  - prebuilt-read
  - prebuilt-layout
  - prebuilt-invoice (and all other available prebuilt base models)
  - custom-models (for custom, you need to label/tag your examples and train the model in the studio. then use the model name here)

take a look at examples-test\test.py for how this can be used in code. for power apps (not tested yet, but i will), you need to send a post req to the endpoint uri and payload with options in the body in an http action. you may notice that there is an option for '"use_vision_api": use_vision_api' in the code above. it's an option i was testing personally, so disregard that. 

</br>

### local setup
a script will be added shortly to do this so no need to be typing or switching screens. but for now, do this:
- git clone https://github.com/DOI-DO/struct-docu-intel-oai.git
- cd .\text-extraction-func
- python -m venv .venv
- .venv\Scripts\activate
- pip install -r requirements.txt
- func start

when you are done, just do `deactivate` or ctrl c or exit whichever way.

note 1: 
if this fails locally: 
- ensure your version of azure function core tool is compatible with version of python used (e.g core tool 4.0 works with python 3.7 to 3.11, and python v3.12 and v3.13 are not supported at the moment - [reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#python-version))
- could also be that the script is not able to find the dependencies because either python or the scripts are not in your path. you can either check your path or manually point it to the path. something like this `func start --python "path to python.exe in your venv."` 

note 2: vscode terminal has character limit, so depending on the size of your documents, the ouput may be truncated. you can get around that by just indexing on the iterable json object response or just use powershell, command prompt or output the result to a text file. an example of the iterable response object is shown in "output.txt"  


*** also note, other payload options will be added as at when needed or called for. however, anyone can hack away or refactor as you deem fit for your needs ***

</br>
dockerfile for simplication and azure deploy will be added shortly (wip)