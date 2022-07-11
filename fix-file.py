import json

DATA_FILE = "data.json"
NEW_DATA_FILE = "foods.json"

def read_data():
    data = []
    with open(DATA_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data

def save_data(data):
    with open(NEW_DATA_FILE, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

def main():
    data = read_data()
    new_data = {}

    for d in data:
        new_data[d["code"]] = {
            "name": d["name"],
            "name_en": d["name_en"],
            "nutrients": d["data"]
        }

    save_data(new_data)

if __name__ == "__main__":
    main()
