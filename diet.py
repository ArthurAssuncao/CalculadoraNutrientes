# see result json in https://www.convertcsv.com/json-to-csv.htm

import json
import matplotlib.pyplot as plot

DIET_FILE = "diet.json"
USER_FILE = "user.json"
DATA_FILE = "foods.json"
FOOD_CUSTOM_DATA_FILE = "foods-custom.json"
DAILY_VALUE_FDA_FILE = "daily-value-fda.json"
DIET_CALCULATED_FILE = "diet-calculated.json"
BIOACTIVE_COMPOUND_FILE = "food_bioactive_compound.json"

ONE_GRAM_MACRO_TO_CALORIES = {
    "protein": 4,
    "carbohydrate": 4,
    "fat": 9,
    "fiber": 2,
    "alcohol": 7
}

NUTRIENTS_NAME_FIXED = {
    'Tiamina': 'Tiamina (Vitamina B1)',
    'Riboflavina': 'Riboflavina (Vitamina B2)',
    'Niacina': 'Niacina (Vitamina B3)',
    'Vitamina B6': 'Piridoxina (Vitamina B6)',
    'Vitamina B12': 'Cobalamina (Vitamina B12)'
}


def read_user():
    data = []
    with open(USER_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data


def user_targets(user):
    if (user["diet_type"] == "maintenance" or user["diet_type"] == "gain"):
        user["protein_target"] = {"unit": "g", "value": float(user["weigth"]) * 1.6}
    else:
        user["protein_target"] = {"unit": "g", "value": float(user["weigth"]) * 2}


def read_diet():
    data = []
    with open(DIET_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data


def read_data():
    data = []
    with open(DATA_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data

def read_food_custom_data():
    data = []
    with open(FOOD_CUSTOM_DATA_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data

def read_daily_value_fda():
    data = []
    with open(DAILY_VALUE_FDA_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    return data


def save_data(data):
    with open(DIET_CALCULATED_FILE, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, sort_keys=False, indent=4)


def calc_value_in_100g(nutrient_base, nutrient_diet):
    if (isinstance(nutrient_base["value"], str)):
        return 0

    value_per_unit = float(nutrient_base["value"]) / 100.0
    value_fixed = float(nutrient_diet["value"]) * value_per_unit
    value_fixed = round(value_fixed, 2)
    return value_fixed


def calc_grams_total(diet_calculated):
    carbohydrate_value = diet_calculated["Carboidrato total"]["value"]
    protein_value = diet_calculated["Proteína"]["value"]
    lipids_value = diet_calculated["Lipídios"]["value"]
    alcohol_value = diet_calculated["Álcool"]["value"]
    ashes_value = diet_calculated["Cinzas"]["value"]

    return carbohydrate_value + protein_value + lipids_value + alcohol_value + ashes_value


def calc_grams_total_with_water(diet_calculated):
    carbohydrate_value = diet_calculated["Carboidrato total"]["value"]
    protein_value = diet_calculated["Proteína"]["value"]
    lipids_value = diet_calculated["Lipídios"]["value"]
    alcohol_value = diet_calculated["Álcool"]["value"]
    ashes_value = diet_calculated["Cinzas"]["value"]
    humidity_value = diet_calculated["Umidade"]["value"]

    return carbohydrate_value + protein_value + lipids_value + alcohol_value + ashes_value + humidity_value


def calc_macros_calories_perc(diet_calculated):
    calories = diet_calculated["Energia"]["value"]
    fiber_calories_perc = 100 * (diet_calculated["Fibra alimentar"]["value"] * ONE_GRAM_MACRO_TO_CALORIES["fiber"]) / calories
    carbo_calories_perc = (100 * (diet_calculated["Carboidrato disponível"]["value"]
                                  * ONE_GRAM_MACRO_TO_CALORIES["carbohydrate"]) / calories) + fiber_calories_perc
    protein_calories_perc = 100 * (diet_calculated["Proteína"]["value"] * ONE_GRAM_MACRO_TO_CALORIES["protein"]) / calories
    fat_calories_perc = 100 * (diet_calculated["Lipídios"]["value"] * ONE_GRAM_MACRO_TO_CALORIES["fat"]) / calories
    alcohol_calories_perc = 100 * (diet_calculated["Álcool"]["value"] * ONE_GRAM_MACRO_TO_CALORIES["alcohol"]) / calories
    rest = 100 - (carbo_calories_perc + protein_calories_perc + fat_calories_perc + alcohol_calories_perc)

    return {
        "Carboidrato": float('{0:.2f}'.format(carbo_calories_perc)),
        "Proteína": float('{0:.2f}'.format(protein_calories_perc)),
        "Lipídios": float('{0:.2f}'.format(fat_calories_perc)),
        "Álcool": float('{0:.2f}'.format(alcohol_calories_perc)),
        "Não identificado": float('{0:.2f}'.format(rest))
    }


def calc_macros_grams_perc(diet_calculated):
    grams = diet_calculated["Carboidrato total"]["value"] + diet_calculated["Proteína"]["value"] + \
        diet_calculated["Lipídios"]["value"] + diet_calculated["Álcool"]["value"] + diet_calculated["Cinzas"]["value"]
    fiber_calories_perc = 100 * diet_calculated["Fibra alimentar"]["value"] / grams
    carbo_calories_perc = (100 * diet_calculated["Carboidrato disponível"]["value"] / grams) + fiber_calories_perc
    protein_calories_perc = 100 * diet_calculated["Proteína"]["value"] / grams
    fat_calories_perc = 100 * diet_calculated["Lipídios"]["value"] / grams
    alcohol_calories_perc = 100 * diet_calculated["Álcool"]["value"] / grams
    rest = 100 - (carbo_calories_perc + protein_calories_perc + fat_calories_perc + alcohol_calories_perc)

    return {
        "Carboidrato": float('{0:.2f}'.format(carbo_calories_perc)),
        "Proteína": float('{0:.2f}'.format(protein_calories_perc)),
        "Lipídios": float('{0:.2f}'.format(fat_calories_perc)),
        "Álcool": float('{0:.2f}'.format(alcohol_calories_perc)),
        "Não identificado": float('{0:.2f}'.format(rest))
    }


def calc_daily_value(user, diet_calculated):
    new_diet_calculated = diet_calculated.copy()
    data_daily_value = read_daily_value_fda()
    nutrients_user = ['Proteína', 'Umidade', 'Energia']
    for nutrient in new_diet_calculated.keys():
        try:
            if (nutrient not in nutrients_user and new_diet_calculated[nutrient]["unit"] != data_daily_value[nutrient]["unit"]):
                msg_error = f'Unidade diferente {new_diet_calculated[nutrient]["unit"]} e {data_daily_value["unit"]}'
                print(msg_error)
                raise ValueError(msg_error)
            diet_value = new_diet_calculated[nutrient]["value"]
            if (nutrient == "Proteína"):
                daily_value = user["protein_target"]["value"]
            elif (nutrient == "Umidade"):
                daily_value = user["water_target"]["value"]
            elif (nutrient == "Energia"):
                daily_value = user["energy_target"]["value"]
            else:
                daily_value = data_daily_value[nutrient]["value"]
            value_perc = (diet_value * 100) / daily_value
            value_perc = round(value_perc, 2)
            new_diet_calculated[nutrient]["daily_value_perc"] = value_perc
        except KeyError:
            print(f"{nutrient} não encontrado no arquivo de valor diário")
        except ZeroDivisionError:
            new_diet_calculated[nutrient]["daily_value_perc"] = 0

    new_diet_calculated["Quantidade em gramas"] = {
        "Total sem Umidade": calc_grams_total(new_diet_calculated),
        "Total com Umidade": calc_grams_total_with_water(new_diet_calculated)
    }
    new_diet_calculated["Percentual de calorias por macro"] = calc_macros_calories_perc(new_diet_calculated)
    new_diet_calculated["Percentual de gramas por macro"] = calc_macros_grams_perc(new_diet_calculated)
    return new_diet_calculated


def fix_nutrients_names(diet_calculated):
    new_diet_calculated = diet_calculated.copy()
    for nutrient in NUTRIENTS_NAME_FIXED.keys():
        new_nutrient_name = NUTRIENTS_NAME_FIXED[nutrient]
        new_diet_calculated[new_nutrient_name] = new_diet_calculated.pop(nutrient)
    return new_diet_calculated


def fix_fields_names(diet_calculated):
    new_diet_calculated = diet_calculated.copy()
    for nutrient in diet_calculated:
        old_nutrient = new_diet_calculated.pop(nutrient)
        new_diet_calculated[nutrient] = {}
        if "unit" in old_nutrient:
            new_diet_calculated[nutrient]["unidade"] = old_nutrient["unit"]
        if "value" in old_nutrient:
            new_diet_calculated[nutrient]["valor"] = old_nutrient["value"]
        if "daily_value_perc" in old_nutrient:
            new_diet_calculated[nutrient]["Percentual do valor diário (VD)"] = old_nutrient["daily_value_perc"]
        if nutrient not in new_diet_calculated or new_diet_calculated[nutrient] == {}:
            new_diet_calculated[nutrient] = old_nutrient
    return new_diet_calculated


def calculate_diet(diet, foods):
    diet_calculated = {}
    # percorre as refeições na dieta da pessoa
    for meal in diet:
        # percorre os alimentos na refeição
        for food in meal['foods'].keys():
            # percorre os nutrientes no alimento da base de dados
            for nutrient in foods[food]["nutrients"].keys():
                nutrient_base = foods[food]["nutrients"][nutrient]
                nutrient_diet = meal['foods'][food]

                food_value = calc_value_in_100g(nutrient_base, nutrient_diet)

                if nutrient not in diet_calculated:
                    diet_calculated[nutrient] = {"unit": nutrient_base["unit"], "value": food_value}
                else:
                    if (diet_calculated[nutrient]["unit"] != nutrient_base["unit"]):
                        raise ValueError(f'Unidade diferente {diet_calculated[nutrient]["unit"]} e {nutrient_base["unit"]}')
                    diet_calculated[nutrient]["value"] = diet_calculated[nutrient]["value"] + food_value
                    diet_calculated[nutrient]["value"] = round(diet_calculated[nutrient]["value"], 2)
    return diet_calculated


def macros_per_meal(diet, foods):
    macros_calculated = {}
    MACROS = ["Proteína", "Carboidrato total", "Carboidrato disponível", "Fibra alimentar", "Energia", "Umidade", "Lipídios"]
    # percorre as refeições na dieta da pessoa
    for meal in diet:
        meal_name = meal["name"]
        macros_calculated[meal_name] = {}
        # percorre os alimentos na refeição
        for food in meal['foods'].keys():
            # percorre os nutrientes no alimento da base de dados
            for nutrient in foods[food]["nutrients"].keys():
                if (nutrient in MACROS):
                    nutrient_base = foods[food]["nutrients"][nutrient]
                    nutrient_diet = meal['foods'][food]

                    food_value = calc_value_in_100g(nutrient_base, nutrient_diet)

                    if nutrient not in macros_calculated[meal_name]:
                        macros_calculated[meal_name][nutrient] = {"unit": nutrient_base["unit"], "value": food_value}
                    else:
                        if (macros_calculated[meal_name][nutrient]["unit"] != nutrient_base["unit"]):
                            raise ValueError(f'Unidade diferente {macros_calculated[meal_name][nutrient]["unit"]} e {nutrient_base["unit"]}')
                        macros_calculated[meal_name][nutrient]["value"] = macros_calculated[meal_name][nutrient]["value"] + food_value
                        macros_calculated[meal_name][nutrient]["value"] = round(macros_calculated[meal_name][nutrient]["value"], 2)
    return macros_calculated


def add_macros_per_meal(diet, foods, diet_calculated):
    new_diet_calculated = diet_calculated.copy()
    diet_macros_per_meal = macros_per_meal(diet, foods)

    new_diet_calculated["Macros por Refeição"] = diet_macros_per_meal

    return new_diet_calculated


def search_word_in_list(word, list):
    for item in list:
        # print(word, item)
        if word.lower() in item.lower():
            return item
    return None


def generate_bioactive_compound_calculated(diet):
    bioactive_compound_data = {}
    data = []
    with open(BIOACTIVE_COMPOUND_FILE, 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())
    foods = data.keys()
    for meal in diet:
        for food_id in meal['foods'].keys():
            food_value = meal['foods'][food_id]["value"]
            food_name = meal['foods'][food_id]["name"]
            food_finded = search_word_in_list(food_name, foods)
            if food_finded:
                bioactive_compounds = data[food_finded].keys()
                for bioactive_compound in bioactive_compounds:
                    bioactive_compound_value = data[food_finded][bioactive_compound]["value"]
                    if bioactive_compound not in bioactive_compound_data:
                        bioactive_compound_data[bioactive_compound] = 0
                    food_proportion_100mg = float(food_value) / 100.0

                    bioactive_compound_data[bioactive_compound] = bioactive_compound_data[bioactive_compound] + \
                        food_proportion_100mg * bioactive_compound_value
                    bioactive_compound_data[bioactive_compound] = round(bioactive_compound_data[bioactive_compound], 2)
    return bioactive_compound_data


def generate_chart(diet_calculated):
    diet = diet_calculated["diet"]
    x = []
    y = []
    label = []
    num_nutrients = 0
    for nutrient in diet:
        try:
            valor_perc = diet[nutrient]["Percentual do valor diário (VD)"]
            num_nutrients = num_nutrients + 1
            label.append(nutrient)
            y.append(valor_perc)
        except KeyError:
            pass

    x = list(range(1, num_nutrients + 1))

    fig = plot.figure()
    fig.set_figwidth(12)
    fig.set_figheight(6)

    plot.bar(x, y, tick_label=label, width=0.8, color=['#19aade', '#7d3ac1'])

    plot.hlines(100, 0, num_nutrients + 1, color='#ff6961', linestyle='dotted', linewidth=2)

    plot.xticks(rotation='vertical')

    plot.xlabel('Nutriente')

    plot.ylabel('% em relação ao Valor Diário')

    plot.subplots_adjust(bottom=0.5)

    plot.title('Porcentagem do valor diário por nutriente!')

    plot.savefig('diet_calculated_nutrients-perc.png', dpi=100)


def main():
    user = read_user()
    diet = read_diet()
    foods = read_data()
    foods_custom = read_food_custom_data()
    all_foods = {**foods, **foods_custom}

    user_targets(user)

    diet_calculated = calculate_diet(diet, all_foods)
    diet_calculated = calc_daily_value(user, diet_calculated)
    diet_calculated = fix_nutrients_names(diet_calculated)
    diet_calculated = fix_fields_names(diet_calculated)
    diet_calculated = {
        "diet": diet_calculated
    }
    diet_calculated = add_macros_per_meal(diet, all_foods, diet_calculated)
    bioactive_calculated = generate_bioactive_compound_calculated(diet)
    diet_calculated['Compostos bioativos - Flavonóides (mg)'] = bioactive_calculated

    generate_chart(diet_calculated)

    save_data(diet_calculated)


if __name__ == "__main__":
    main()
