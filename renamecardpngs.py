import os

# adjust these to match whatever naming format your downloaded files use
old_to_new = {
    "ace": "A",
    "king": "K", 
    "queen": "Q",
    "jack": "J",
    "hearts2": "h",
    "diamonds2": "d",
    "clubs2": "c",
    "spades2": "s",
    "10": "T",
    "9": "9",
    "8": "8",
    "7": "7",
    "6": "6",
    "5": "5",
    "4": "4",
    "3": "3",
    "2": "2",
    "hearts": "h",
    "diamonds": "d",
    "clubs": "c",
    "spades": "s",
    
}

if __name__ == "__main__":
    folder = "cards"

    for filename in os.listdir(folder):
        if not filename.endswith(".png"):
            continue

        new_name = filename.lower()  
        for old, new in old_to_new.items():
            new_name = new_name.replace(old, new)

        new_name = new_name.replace("_of_", "").replace("_", "").replace("-", "")

        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)

        print(f"{filename} → {new_name}")
        os.rename(old_path, new_path)

    print("done")