import sys
import os
import argparse
import webbrowser

data_to_analyze = {}
analyzed = {}
opts = {}
PROJECT_URL = "https://github.com/TooFar42/CodeSniffer/"
OPTS_PATH = os.path.join(os.path.expanduser("~"), ".sniffcode", "opts.txt")
MODELS = ["qwen3.5:0.8b-q8_0", "llama3.2:1b", "gemma4:e2b", "gemma4:e4b"]

def load():
    global opts
    if not os.path.exists(OPTS_PATH):
        os.makedirs(os.path.dirname(OPTS_PATH), exist_ok=True)
        print("This is the first time running this tool, we'll setup the system for you.")
        print("Please awnser these questions first: ")
        name = input("\n1 ) What's your name? How are we going to call you? -> ")
        ram = float(input("\n2 ) How much ram or vram are you going to dedicate to this tool? input numbers (gb) -> "))
        try:
            import torch.cuda as c
            cuda_av = True if c.is_available() else False
        except Exception:
            cuda_av = False
        ramlvl = 0
        if ram > 1:
            ramlvl = 1
        if ram > 2:
            ramlvl = 2
        if ram > 3 and cuda_av:
            ramlvl = 3
        leave_a_star = input("Would you like to leave a star to the github repo? (Y/N) -> ")
        if leave_a_star == "Y":
            webbrowser.open(PROJECT_URL)
        opts = {"AI_access": ramlvl, "name": name}
        print("SETUP COMPLETE!")
        print("run this again to sniff your first codebase! ")
        save()
        sys.exit()

    with open(OPTS_PATH, "r") as f:
        data = f.readlines()
        for d in data:
            o = d.split("=")
            opts[o[0].strip()] = o[1].strip()

def save():
    with open(OPTS_PATH, "w") as f:
        lines = []
        for o in opts:
            lines.append(f"{o} = {opts[o]}\n")
        f.writelines(lines)


ollama_av = True
try:
    import ollama
except Exception:
    ollama_av = False
    sys.exit()


def scan(dir):
    data_to_analyze.clear()
    files = os.listdir(dir)
    if len(files) != 0:
        for file in files:
            if file.endswith((".py", ".cpp", ".js", ".ts", ".c", ".h")):
                pth = os.path.join(dir, file)
                with open(pth, "r") as f:
                    data_to_analyze[pth] = (f.read())
    else:
        print("No files to analyze")
        sys.exit()
    if len(data_to_analyze) == 0:
        print("No supported files found to analyze.")
        sys.exit()

def review():
    model = MODELS[0]
    if int(opts["AI_access"]) == 1:
        model = MODELS[1]
    if int(opts["AI_access"]) == 2:
        model = MODELS[2]
    if int(opts["AI_access"]) == 3:
        model = MODELS[3]
    ollama.pull(model)
    marks = []
    for data in data_to_analyze:
        try:
            mark = float(ollama.generate(model, "Analyze this: " + data_to_analyze[data] + "; Ok now ouput a number, 1 to 10, a score. No text allowed, just output the number")["response"].strip())
        except Exception:
            mark = 0.0
        marks.append(mark)
    code_reviews = []
    for data in data_to_analyze:
        rev = ollama.generate(model, "Analyze this: " + data_to_analyze[data] + "; Ok now ouput a 5 line review for this codabase. Just output the review, don't output any unnecessary text please.")["response"].strip()
        code_reviews.append(rev)
    
    files = list(data_to_analyze.keys())
    for i in range(len(marks)):
        analyzed[files[i]] = [marks[i], code_reviews[i]]

def main():
    load()
    parser = argparse.ArgumentParser(description="SniffCode")
    parser.add_argument("directory", type=str, help="The directory to analyze.")
    args = parser.parse_args()
    scan(args.directory)
    review()
    print("Finished analyzing!")
    for a in analyzed:
        print(f"Review for {a}")
        print(f"Text review: \n {analyzed[a][1]}\n")
        print(f"Overall score: {analyzed[a][0]}\n\n")
        


if __name__ == "__main__":
    try:
        main()
    except Exception:
        save()
